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
    """学生个人信息更新请求模型"""
    name: Optional[str] = Field(None, description="真实姓名", example="张三")
    gender: Optional[str] = Field(None, description="性别", example="男")
    age: Optional[int] = Field(None, description="年龄，18-100岁", example=22, ge=18, le=100)
    toefl: Optional[float] = Field(None, description="托福成绩，0-120分", example=105.0, ge=0, le=120)
    gre: Optional[float] = Field(None, description="GRE成绩，260-340分", example=320.0, ge=260, le=340)
    gpa: Optional[float] = Field(None, description="GPA成绩，0.0-4.0分", example=3.5, ge=0, le=4.0)
    target_region: Optional[str] = Field(None, description="目标留学地区", example="美国")
    email: Optional[str] = Field(None, description="电子邮箱", example="zhangsan@example.com")
    phone: Optional[str] = Field(None, description="手机号码", example="13800138000")

class SchoolResponse(BaseModel):
    """学校信息响应模型"""
    id: int = Field(..., description="学校ID")
    chinese_name: str = Field(..., description="学校中文名称", example="哈佛大学")
    english_name: str = Field(..., description="学校英文名称", example="Harvard University")
    location: str = Field(..., description="学校所在地", example="美国马萨诸塞州")
    ranking: int = Field(..., description="学校排名", example=1)
    introduction: str = Field(..., description="学校简介")
    details: str = Field(..., description="学校详细信息")
    majors: List[dict] = Field(default_factory=list, description="学校专业信息列表")
    recommendation_score: Optional[float] = Field(None, description="推荐分数，基于学生成绩计算", example=85.5)

class TrainingReserveRequest(BaseModel):
    """语言培训预约请求模型"""
    teacher_id: Optional[int] = Field(None, description="教师ID，不指定则由系统分配")
    total_hours: int = Field(..., gt=0, description="总课时数", example=20)
    training_type: Optional[str] = Field(None, description="培训类型", example="托福培训")
    notes: Optional[str] = Field(None, description="备注信息", example="希望重点辅导听力部分")

class DocumentReserveRequest(BaseModel):
    """文书润色预约请求模型"""
    teacher_id: int = Field(..., description="教师ID", example=2)
    document_count: int = Field(..., gt=0, description="文档数量", example=3)
    document_type: Optional[str] = Field(None, description="文档类型", example="个人陈述")
    target_school: Optional[str] = Field(None, description="目标学校", example="哈佛大学")
    notes: Optional[str] = Field(None, description="备注信息", example="希望突出科研经历")

# 获取个人信息
@router.get("/profile", response_model=dict, summary="获取个人信息", description="获取当前登录学生的个人详细信息")
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
@router.put("/profile", response_model=dict, summary="更新个人信息", description="更新当前登录学生的个人信息，只更新非空字段")
def update_profile(request: StudentProfileUpdate, current_user: User = Depends(get_current_student), db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="个人信息不存在"
        )
    
    try:
        # 更新非空字段
        update_data = request.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)
        
        db.commit()
        db.refresh(profile)
        
        return {"message": "个人信息更新成功"}
    except Exception as e:
        db.rollback()
        # 记录详细错误信息
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"学生信息更新失败: {str(e)}", exc_info=True)
        # 返回通用错误消息，不泄露敏感信息
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新失败，请稍后重试"
        )

# 获取学校推荐
@router.get("/recommendation", response_model=List[SchoolResponse], summary="获取学校推荐", description="基于学生的托福、GRE、GPA成绩和目标地区，推荐合适的留学学校")
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
        toefl_requirement = 110 - (school.ranking * 0.2) if school.ranking else 90
        gre_requirement = 330 - (school.ranking * 0.1) if school.ranking else 300
        gpa_requirement = 3.8 - (school.ranking * 0.002) if school.ranking else 3.5
        
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
                {"major_name": major.major_name, "major_rank": major.major_rank}
                for major in school.majors
            ]
            
            results.append({
                "id": school.id,
                "chinese_name": school.chinese_name,
                "english_name": school.english_name,
                "location": school.location,
                "ranking": school.ranking,
                "introduction": school.introduction,
                "details": school.details,
                "majors": majors,
                "recommendation_score": round(recommendation_score, 2)
            })
    
    # 按推荐系数降序排序
    results.sort(key=lambda x: x["recommendation_score"], reverse=True)
    
    return results

# 查找学校
@router.get("/search-schools", response_model=List[SchoolResponse], summary="查找学校", description="根据学校名称、专业名称或地区搜索学校信息")
def search_schools(
    name: Optional[str] = Query(None, description="学校名称搜索关键词", example="哈佛"),
    major: Optional[str] = Query(None, description="专业名称搜索关键词", example="计算机"),
    region: Optional[str] = Query(None, description="地区搜索关键词", example="美国"),
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
            {"major_name": m.major_name, "major_rank": m.major_rank}
            for m in school.majors
        ]
        
        results.append({
            "id": school.id,
            "chinese_name": school.chinese_name,
            "english_name": school.english_name,
            "location": school.location,
            "ranking": school.ranking,
                "introduction": school.introduction,
                "details": school.details,
            "majors": majors
        })
    
    return results

# 获取学校列表
@router.get("/schools", response_model=List[SchoolResponse], summary="获取学校列表", description="获取所有学校列表，用于学校推荐和查询")
def get_schools(current_user: User = Depends(get_current_student), db: Session = Depends(get_db)):
    # 查询所有学校
    schools = db.query(School).all()
    results = []
    
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
            "ranking": school.ranking,
            "introduction": school.introduction,
            "details": school.details,
            "majors": majors
        })
    
    return results

# 获取学校详情
@router.get("/school/{school_id}", response_model=SchoolResponse, summary="获取学校详情", description="根据学校ID获取指定学校的详细信息，包括基本信息和专业设置")
def get_school_detail(school_id: int, current_user: User = Depends(get_current_student), db: Session = Depends(get_db)):
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
            "ranking": school.ranking,
            "introduction": school.introduction,
            "details": school.details,
        "majors": majors
    }

# 获取成功案例
@router.get("/success-cases", response_model=List[dict], summary="获取成功案例", description="获取所有留学申请成功案例")
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
@router.post("/training/reserve", response_model=dict, summary="预约语言培训", description="为当前学生预约语言培训服务，可指定教师或由系统分配")
def reserve_training(request: TrainingReserveRequest, current_user: User = Depends(get_current_student), db: Session = Depends(get_db)):
    # 创建预约，使用请求中的teacher_id值（如果提供）
    reservation = TrainingReservation(
        student_id=current_user.id,
        teacher_id=request.teacher_id,  # 使用请求中的教师ID
        total_hours=request.total_hours,
        training_type=request.training_type,
        notes=request.notes,
        status="pending"
    )
    
    db.add(reservation)
    db.commit()
    
    return {"message": "预约成功", "reservation_id": reservation.id}

# 获取培训预约列表
@router.get("/training/list", response_model=List[dict], summary="获取培训预约列表", description="获取当前学生的所有语言培训预约记录")
def get_training_list(current_user: User = Depends(get_current_student), db: Session = Depends(get_db)):
    reservations = db.query(TrainingReservation).filter(
        TrainingReservation.student_id == current_user.id
    ).all()
    
    # 获取教师信息并添加到返回数据中
    results = []
    for r in reservations:
        # 获取教师信息
        teacher = db.query(User).filter(User.id == r.teacher_id).first()
        teacher_name = teacher.username if teacher else '未分配'
        
        results.append({
            "id": r.id,
            "training_type": r.training_type or '语言培训',
            "teacher_id": r.teacher_id,
            "teacher_name": teacher_name,
            "total_hours": r.total_hours,
            "completed_hours": r.attended_hours,  # 前端使用completed_hours字段
            "status": r.status,
            "feedback": r.feedback,
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    
    return results

# 获取培训预约详情
@router.get("/training/detail", response_model=dict, summary="获取培训预约详情", description="获取指定ID的语言培训预约详细信息")
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
@router.post("/document/reserve", response_model=dict, summary="预约文书润色", description="为当前学生预约文书润色服务，需要指定教师")
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
@router.get("/document/list", response_model=List[dict], summary="获取文书预约列表", description="获取当前学生的所有文书润色预约记录")
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
@router.get("/document/detail", response_model=dict, summary="获取文书预约详情", description="获取指定ID的文书润色预约详细信息")
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