from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from utils.database import get_db
from utils.dependencies import get_current_student
from models.database import User, StudentProfile, School, SchoolMajor, SuccessCase, TrainingReservation, DocumentReservation
from pydantic import BaseModel, Field

router = APIRouter(prefix="/student", tags=["留学生服务"])

# 数据模型
class StudentProfileUpdate(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    toefl: Optional[float] = None
    gre: Optional[float] = None
    gpa: Optional[float] = None
    target_region: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

class SchoolResponse(BaseModel):
    id: int
    chinese_name: str
    english_name: str
    location: str
    rank: int
    basic_info: str
    detailed_info: str
    majors: List[dict] = []
    recommendation_score: Optional[float] = None

class TrainingReserveRequest(BaseModel):
    teacher_id: int
    total_hours: int = Field(..., gt=0)
    training_type: Optional[str] = None
    notes: Optional[str] = None

class DocumentReserveRequest(BaseModel):
    teacher_id: int
    document_count: int = Field(..., gt=0)
    document_type: Optional[str] = None
    target_school: Optional[str] = None
    notes: Optional[str] = None

# 获取个人信息
@router.get("/profile", response_model=dict)
def get_profile(current_user: User = Depends(get_current_student), db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="个人信息不存在"
        )
    
    return {
        "id": profile.id,
        "name": profile.name,
        "gender": profile.gender,
        "age": profile.age,
        "toefl": profile.toefl,
        "gre": profile.gre,
        "gpa": profile.gpa,
        "target_region": profile.target_region,
        "email": profile.email,
        "phone": profile.phone
    }

# 更新个人信息
@router.put("/profile", response_model=dict)
def update_profile(request: StudentProfileUpdate, current_user: User = Depends(get_current_student), db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="个人信息不存在"
        )
    
    # 更新非空字段
    update_data = request.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    db.commit()
    db.refresh(profile)
    
    return {"message": "个人信息更新成功"}

# 获取学校推荐
@router.get("/recommendation", response_model=List[SchoolResponse])
def get_recommendations(current_user: User = Depends(get_current_student), db: Session = Depends(get_db)):
    # 获取学生信息
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile or not (profile.toefl and profile.gre and profile.gpa):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请先完善托福、GRE、GPA成绩信息"
        )
    
    # 查询符合条件的学校
    query = db.query(School)
    if profile.target_region:
        query = query.filter(School.location.contains(profile.target_region))
    
    schools = query.all()
    results = []
    
    for school in schools:
        # 计算推荐系数
        # 基于学校排名反推录取要求
        toefl_requirement = 110 - (school.rank * 0.2) if school.rank else 90
        gre_requirement = 330 - (school.rank * 0.1) if school.rank else 300
        gpa_requirement = 3.8 - (school.rank * 0.002) if school.rank else 3.5
        
        # 计算各项匹配度
        toefl_score = min(profile.toefl / toefl_requirement * 100, 100)
        gre_score = min(profile.gre / gre_requirement * 100, 100)
        gpa_score = min(profile.gpa / gpa_requirement * 100, 100)
        
        # 计算最终推荐系数（权重：托福30%+GRE30%+GPA40%）
        recommendation_score = toefl_score * 0.3 + gre_score * 0.3 + gpa_score * 0.4
        
        # 只返回推荐系数≥60的学校
        if recommendation_score >= 60:
            # 获取专业信息
            majors = [
                {"name": major.major_name, "rank": major.major_rank}
                for major in school.majors
            ]
            
            results.append({
                "id": school.id,
                "chinese_name": school.chinese_name,
                "english_name": school.english_name,
                "location": school.location,
                "rank": school.rank,
                "basic_info": school.basic_info,
                "detailed_info": school.detailed_info,
                "majors": majors,
                "recommendation_score": round(recommendation_score, 2)
            })
    
    # 按推荐系数降序排序
    results.sort(key=lambda x: x["recommendation_score"], reverse=True)
    
    return results

# 查找学校
@router.get("/search-schools", response_model=List[SchoolResponse])
def search_schools(
    name: Optional[str] = Query(None, description="学校名称"),
    major: Optional[str] = Query(None, description="专业名称"),
    region: Optional[str] = Query(None, description="地区"),
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    query = db.query(School)
    
    # 按名称搜索
    if name:
        query = query.filter(
            (School.chinese_name.contains(name)) |
            (School.english_name.contains(name))
        )
    
    # 按地区搜索
    if region:
        query = query.filter(School.location.contains(region))
    
    schools = query.all()
    results = []
    
    # 如果按专业搜索，需要进一步过滤
    if major:
        filtered_schools = []
        for school in schools:
            has_major = any(m.major_name.contains(major) for m in school.majors)
            if has_major:
                filtered_schools.append(school)
        schools = filtered_schools
    
    for school in schools:
        majors = [
            {"name": m.major_name, "rank": m.major_rank}
            for m in school.majors
        ]
        
        results.append({
            "id": school.id,
            "chinese_name": school.chinese_name,
            "english_name": school.english_name,
            "location": school.location,
            "rank": school.rank,
            "basic_info": school.basic_info,
            "detailed_info": school.detailed_info,
            "majors": majors
        })
    
    return results

# 获取学校详情
@router.get("/school", response_model=SchoolResponse)
def get_school(school_id: int, current_user: User = Depends(get_current_student), db: Session = Depends(get_db)):
    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学校不存在"
        )
    
    majors = [
        {"name": m.major_name, "rank": m.major_rank}
        for m in school.majors
    ]
    
    return {
        "id": school.id,
        "chinese_name": school.chinese_name,
        "english_name": school.english_name,
        "location": school.location,
        "rank": school.rank,
        "basic_info": school.basic_info,
        "detailed_info": school.detailed_info,
        "majors": majors
    }

# 获取成功案例
@router.get("/success-cases", response_model=List[dict])
def get_success_cases(current_user: User = Depends(get_current_student), db: Session = Depends(get_db)):
    cases = db.query(SuccessCase).all()
    return [
        {
            "id": case.id,
            "title": case.title,
            "content": case.content,
            "has_file": bool(case.file_path)
        }
        for case in cases
    ]

# 预约语言培训
@router.post("/training/reserve", response_model=dict)
def reserve_training(request: TrainingReserveRequest, current_user: User = Depends(get_current_student), db: Session = Depends(get_db)):
    # 验证教师是否存在
    teacher = db.query(User).filter(User.id == request.teacher_id, User.role == "teacher").first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="教师不存在"
        )
    
    # 创建预约
    reservation = TrainingReservation(
        student_id=current_user.id,
        teacher_id=request.teacher_id,
        total_hours=request.total_hours,
        training_type=request.training_type,
        notes=request.notes,
        status="pending"
    )
    
    db.add(reservation)
    db.commit()
    
    return {"message": "预约成功", "reservation_id": reservation.id}

# 查看培训预约列表
@router.get("/training/list", response_model=List[dict])
def get_training_list(current_user: User = Depends(get_current_student), db: Session = Depends(get_db)):
    reservations = db.query(TrainingReservation).filter(
        TrainingReservation.student_id == current_user.id
    ).all()
    
    return [
        {
            "id": r.id,
            "teacher_id": r.teacher_id,
            "total_hours": r.total_hours,
            "attended_hours": r.attended_hours,
            "status": r.status,
            "feedback": r.feedback,
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        for r in reservations
    ]

# 获取培训预约详情
@router.get("/training/detail", response_model=dict)
def get_training_detail(id: int, current_user: User = Depends(get_current_student), db: Session = Depends(get_db)):
    reservation = db.query(TrainingReservation).filter(
        TrainingReservation.id == id,
        TrainingReservation.student_id == current_user.id
    ).first()
    
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预约记录不存在"
        )
    
    # 获取教师信息
    teacher = db.query(User).filter(User.id == reservation.teacher_id).first()
    teacher_name = teacher.username if teacher else '未分配'
    
    return {
        "id": reservation.id,
        "training_type": reservation.training_type or '语言培训',
        "total_hours": reservation.total_hours,
        "completed_hours": reservation.attended_hours,
        "teacher_name": teacher_name,
        "status": reservation.status,
        "notes": reservation.notes,
        "feedback": reservation.feedback,
        "homework": reservation.homework,
        "created_at": reservation.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": reservation.updated_at.strftime("%Y-%m-%d %H:%M:%S") if reservation.updated_at else None
    }

# 预约文书润色
@router.post("/document/reserve", response_model=dict)
def reserve_document(request: DocumentReserveRequest, current_user: User = Depends(get_current_student), db: Session = Depends(get_db)):
    # 验证教师是否存在
    teacher = db.query(User).filter(User.id == request.teacher_id, User.role == "teacher").first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="教师不存在"
        )
    
    # 创建预约
    reservation = DocumentReservation(
        student_id=current_user.id,
        teacher_id=request.teacher_id,
        document_count=request.document_count,
        document_type=request.document_type,
        target_school=request.target_school,
        notes=request.notes,
        status="pending",
        progress=0
    )
    
    db.add(reservation)
    db.commit()
    
    return {"message": "预约成功", "reservation_id": reservation.id}

# 查看文书预约列表
@router.get("/document/list", response_model=List[dict])
def get_document_list(current_user: User = Depends(get_current_student), db: Session = Depends(get_db)):
    reservations = db.query(DocumentReservation).filter(
        DocumentReservation.student_id == current_user.id
    ).all()
    
    results = []
    for r in reservations:
        # 获取教师信息
        teacher = db.query(User).filter(User.id == r.teacher_id).first()
        teacher_name = teacher.username if teacher else '未分配'
        
        results.append({
            "id": r.id,
            "teacher_id": r.teacher_id,
            "document_type": r.document_type,
            "document_count": r.document_count,
            "target_school": r.target_school,
            "teacher_name": teacher_name,
            "status": r.status,
            "progress": r.progress,
            "revised_content": r.revised_content,
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    
    return results

# 获取文书预约详情
@router.get("/document/detail", response_model=dict)
def get_document_detail(id: int, current_user: User = Depends(get_current_student), db: Session = Depends(get_db)):
    reservation = db.query(DocumentReservation).filter(
        DocumentReservation.id == id,
        DocumentReservation.student_id == current_user.id
    ).first()
    
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预约记录不存在"
        )
    
    # 获取教师信息
    teacher = db.query(User).filter(User.id == reservation.teacher_id).first()
    teacher_name = teacher.username if teacher else '未分配'
    
    return {
        "id": reservation.id,
        "document_type": reservation.document_type or '普通文书',
        "document_count": reservation.document_count,
        "target_school": reservation.target_school or '未指定',
        "teacher_name": teacher_name,
        "status": reservation.status,
        "progress": reservation.progress,
        "revised_content": reservation.revised_content,
        "notes": reservation.notes,
        "comments": reservation.comments,
        "created_at": reservation.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": reservation.updated_at.strftime("%Y-%m-%d %H:%M:%S") if reservation.updated_at else None
    }