from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from utils.database import get_db
from utils.dependencies import get_current_teacher
from models.database import User, TeacherProfile, School, SchoolMajor, TrainingReservation, DocumentReservation, StudentProfile
from pydantic import BaseModel, Field

router = APIRouter(prefix="/teacher", tags=["教师服务"])

# 数据模型
class TeacherProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    subject: Optional[str] = None

class TrainingStatusUpdate(BaseModel):
    reservation_id: int
    status: str  # accepted, rejected

class TrainingProgressUpdate(BaseModel):
    reservation_id: int
    attended_hours: int = Field(..., ge=0)

class TrainingFeedbackUpdate(BaseModel):
    reservation_id: int
    feedback: str

class DocumentStatusUpdate(BaseModel):
    reservation_id: int
    status: str  # accepted, rejected

class DocumentContentUpdate(BaseModel):
    reservation_id: int
    revised_content: str

class DocumentProgressUpdate(BaseModel):
    reservation_id: int
    progress: int = Field(..., ge=0, le=100)

class SchoolAddRequest(BaseModel):
    chinese_name: str
    english_name: str
    location: str
    rank: int
    basic_info: str
    detailed_info: str
    majors: List[dict] = []  # [{"name": "计算机", "rank": 10}]

class SchoolUpdateRequest(BaseModel):
    chinese_name: Optional[str] = None
    english_name: Optional[str] = None
    location: Optional[str] = None
    rank: Optional[int] = None
    basic_info: Optional[str] = None
    detailed_info: Optional[str] = None

# 获取个人信息
@router.get("/profile", response_model=dict)
def get_profile(current_user: User = Depends(get_current_teacher), db: Session = Depends(get_db)):
    profile = db.query(TeacherProfile).filter(TeacherProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="个人信息不存在"
        )
    
    return {
        "id": profile.id,
        "name": profile.name,
        "email": profile.email,
        "phone": profile.phone,
        "subject": profile.subject
    }

# 更新个人信息
@router.put("/profile", response_model=dict)
def update_profile(request: TeacherProfileUpdate, current_user: User = Depends(get_current_teacher), db: Session = Depends(get_db)):
    profile = db.query(TeacherProfile).filter(TeacherProfile.user_id == current_user.id).first()
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
    
    return {"message": "个人信息更新成功"}

# 获取学生统计信息
@router.get("/statistics/student", response_model=dict)
def get_student_statistics(current_user: User = Depends(get_current_teacher), db: Session = Depends(get_db)):
    # 获取所有学生
    student_profiles = db.query(StudentProfile).all()
    
    if not student_profiles:
        return {
            "total_count": 0,
            "male_count": 0,
            "female_count": 0,
            "average_toefl": 0,
            "average_gre": 0,
            "average_gpa": 0
        }
    
    # 统计数据
    total_count = len(student_profiles)
    male_count = sum(1 for p in student_profiles if p.gender == "男")
    female_count = sum(1 for p in student_profiles if p.gender == "女")
    
    # 计算平均分
    toefl_scores = [p.toefl for p in student_profiles if p.toefl]
    gre_scores = [p.gre for p in student_profiles if p.gre]
    gpa_scores = [p.gpa for p in student_profiles if p.gpa]
    
    average_toefl = sum(toefl_scores) / len(toefl_scores) if toefl_scores else 0
    average_gre = sum(gre_scores) / len(gre_scores) if gre_scores else 0
    average_gpa = sum(gpa_scores) / len(gpa_scores) if gpa_scores else 0
    
    return {
        "total_count": total_count,
        "male_count": male_count,
        "female_count": female_count,
        "average_toefl": round(average_toefl, 2),
        "average_gre": round(average_gre, 2),
        "average_gpa": round(average_gpa, 2)
    }

# 留学成功率预测
@router.get("/statistics/predict", response_model=dict)
def predict_success_rate(
    toefl_min: Optional[float] = Query(None, description="最低托福分数"),
    gre_min: Optional[float] = Query(None, description="最低GRE分数"),
    gpa_min: Optional[float] = Query(None, description="最低GPA"),
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    # 模拟历史申请数据（实际应该有专门的applications表）
    # 这里简单地根据学生分数进行模拟计算
    query = db.query(StudentProfile)
    
    if toefl_min:
        query = query.filter(StudentProfile.toefl >= toefl_min)
    if gre_min:
        query = query.filter(StudentProfile.gre >= gre_min)
    if gpa_min:
        query = query.filter(StudentProfile.gpa >= gpa_min)
    
    qualified_students = query.count()
    total_students = db.query(StudentProfile).count()
    
    # 基于分数计算成功率（模拟）
    base_rate = 0.5
    score_bonus = 0
    
    if toefl_min and toefl_min >= 100:
        score_bonus += 0.2
    if gre_min and gre_min >= 320:
        score_bonus += 0.2
    if gpa_min and gpa_min >= 3.5:
        score_bonus += 0.1
    
    success_rate = min(base_rate + score_bonus, 0.95)
    
    return {
        "qualified_students": qualified_students,
        "total_students": total_students,
        "success_rate": round(success_rate * 100, 2)  # 转换为百分比
    }

# 语言培训相关

# 获取培训预约列表
@router.get("/document/list", response_model=List[dict])
def get_document_list(
    status: Optional[str] = Query(None, description="文书状态筛选"),
    student_name: Optional[str] = Query(None, description="学生姓名筛选"),
    document_type: Optional[str] = Query(None, description="文书类型筛选"),
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    # 查询当前教师的文书预约
    query = db.query(DocumentReservation).filter(
        DocumentReservation.teacher_id == current_user.id
    )
    
    # 应用筛选条件
    if status:
        query = query.filter(DocumentReservation.status == status)
    if document_type:
        query = query.filter(DocumentReservation.document_type == document_type)
    if student_name:
        # 子查询：查找姓名匹配的学生ID
        student_ids = db.query(User.id).join(StudentProfile).filter(
            StudentProfile.name.like(f"%{student_name}%")
        ).subquery()
        query = query.filter(DocumentReservation.student_id.in_(student_ids))
    
    # 按创建时间倒序排列
    query = query.order_by(DocumentReservation.created_at.desc())
    
    # 获取结果
    document_reservations = query.all()
    
    # 构建响应数据
    result = []
    for doc in document_reservations:
        # 获取学生信息
        student_profile = db.query(StudentProfile).join(User).filter(
            User.id == doc.student_id
        ).first()
        
        result.append({
            "id": doc.id,
            "student_name": student_profile.name if student_profile else "未知",
            "document_type": doc.document_type,
            "document_count": doc.document_count,
            "target_school": doc.target_school,
            "notes": doc.notes,
            "status": doc.status,
            "progress": doc.progress,
            "created_at": doc.created_at.isoformat() if doc.created_at else None,
            "updated_at": doc.updated_at.isoformat() if doc.updated_at else None
        })
    
    return result

@router.get("/document/detail", response_model=dict)
def get_document_detail(
    id: int = Query(..., description="文书预约ID"),
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    # 查询当前教师的特定文书预约
    document = db.query(DocumentReservation).filter(
        DocumentReservation.id == id,
        DocumentReservation.teacher_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文书预约不存在"
        )
    
    # 获取学生信息
    student_profile = db.query(StudentProfile).join(User).filter(
        User.id == document.student_id
    ).first()
    
    # 构建响应数据
    result = {
        "id": document.id,
        "student_name": student_profile.name if student_profile else "未知",
        "document_type": document.document_type,
        "document_count": document.document_count,
        "target_school": document.target_school,
        "notes": document.notes,
        "comments": document.comments,
        "status": document.status,
        "progress": document.progress,
        "original_content": document.original_content,
        "content": document.revised_content,  # 前端使用content字段
        "file_path": document.file_path,
        "created_at": document.created_at.isoformat() if document.created_at else None,
        "updated_at": document.updated_at.isoformat() if document.updated_at else None
    }
    
    return result

@router.get("/training/list", response_model=List[dict])
def get_training_list(
    status: Optional[str] = Query(None, description="培训状态筛选"),
    student_name: Optional[str] = Query(None, description="学生姓名筛选"),
    training_type: Optional[str] = Query(None, description="培训类型筛选"),
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    # 查询当前教师的培训预约
    query = db.query(TrainingReservation).filter(
        TrainingReservation.teacher_id == current_user.id
    )
    
    # 应用筛选条件
    if status:
        query = query.filter(TrainingReservation.status == status)
    if training_type:
        query = query.filter(TrainingReservation.training_type == training_type)
    if student_name:
        # 子查询：查找姓名匹配的学生ID
        student_ids = db.query(User.id).join(StudentProfile).filter(
            StudentProfile.name.like(f"%{student_name}%")
        ).subquery()
        query = query.filter(TrainingReservation.student_id.in_(student_ids))
    
    # 执行查询
    reservations = query.all()
    
    # 构建响应数据
    result = []
    for reservation in reservations:
        # 获取学生信息
        student = db.query(User).filter(User.id == reservation.student_id).first()
        student_profile = None
        if student:
            student_profile = db.query(StudentProfile).filter(StudentProfile.user_id == student.id).first()
        
        # 构建学生成绩信息
        student_scores = {}
        if student_profile:
            if student_profile.toefl:
                student_scores['toefl'] = student_profile.toefl
            if student_profile.gre:
                student_scores['gre'] = student_profile.gre
            if student_profile.gpa:
                student_scores['gpa'] = student_profile.gpa
        
        result.append({
            "id": reservation.id,
            "student_name": student_profile.name if student_profile else "未知",
            "training_type": reservation.training_type,
            "total_hours": reservation.total_hours,
            "completed_hours": reservation.attended_hours,
            "created_at": reservation.created_at.isoformat() if reservation.created_at else None,
            "status": reservation.status,
            "notes": reservation.notes,
            "feedback": reservation.feedback,
            "student_scores": student_scores if student_scores else None
        })
    
    return result

# 获取培训预约详情
@router.get("/training/detail", response_model=dict)
def get_training_detail(
    id: int = Query(..., description="培训预约ID"),
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    # 查询当前教师的培训预约
    reservation = db.query(TrainingReservation).filter(
        TrainingReservation.id == id,
        TrainingReservation.teacher_id == current_user.id
    ).first()
    
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="培训预约不存在"
        )
    
    # 获取学生信息
    student = db.query(User).filter(User.id == reservation.student_id).first()
    student_profile = None
    if student:
        student_profile = db.query(StudentProfile).filter(StudentProfile.user_id == student.id).first()
    
    # 构建学生成绩信息
    student_scores = {}
    if student_profile:
        if student_profile.toefl:
            student_scores['toefl'] = student_profile.toefl
        if student_profile.gre:
            student_scores['gre'] = student_profile.gre
        if student_profile.gpa:
            student_scores['gpa'] = student_profile.gpa
    
    # 构建响应数据
    result = {
        "id": reservation.id,
        "student_name": student_profile.name if student_profile else "未知",
        "training_type": reservation.training_type,
        "total_hours": reservation.total_hours,
        "completed_hours": reservation.attended_hours,
        "created_at": reservation.created_at.isoformat() if reservation.created_at else None,
        "status": reservation.status,
        "notes": reservation.notes,
        "feedback": reservation.feedback,
        "homework": reservation.homework,
        "reject_reason": None,  # 数据库模型中没有此字段，可以根据需要添加
        "student_scores": student_scores if student_scores else None
    }
    
    return result

# 处理培训预约状态
@router.put("/training/status", response_model=dict)
def update_training_status(request: TrainingStatusUpdate, current_user: User = Depends(get_current_teacher), db: Session = Depends(get_db)):
    reservation = db.query(TrainingReservation).filter(
        TrainingReservation.id == request.reservation_id,
        TrainingReservation.teacher_id == current_user.id
    ).first()
    
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预约不存在"
        )
    
    if reservation.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该预约已处理"
        )
    
    reservation.status = request.status
    db.commit()
    
    return {"message": "状态更新成功"}

# 更新培训进度
@router.put("/training/progress", response_model=dict)
def update_training_progress(request: TrainingProgressUpdate, current_user: User = Depends(get_current_teacher), db: Session = Depends(get_db)):
    reservation = db.query(TrainingReservation).filter(
        TrainingReservation.id == request.reservation_id,
        TrainingReservation.teacher_id == current_user.id
    ).first()
    
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预约不存在"
        )
    
    if reservation.status != "accepted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请先接受预约"
        )
    
    if request.attended_hours > reservation.total_hours:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已上课时不能超过总课时"
        )
    
    reservation.attended_hours = request.attended_hours
    
    # 如果已上完所有课时，自动标记为完成
    if request.attended_hours == reservation.total_hours:
        reservation.status = "completed"
    
    db.commit()
    
    return {"message": "进度更新成功"}

# 添加培训反馈
@router.put("/training/feedback", response_model=dict)
def update_training_feedback(request: TrainingFeedbackUpdate, current_user: User = Depends(get_current_teacher), db: Session = Depends(get_db)):
    reservation = db.query(TrainingReservation).filter(
        TrainingReservation.id == request.reservation_id,
        TrainingReservation.teacher_id == current_user.id
    ).first()
    
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预约不存在"
        )
    
    reservation.feedback = request.feedback
    db.commit()
    
    return {"message": "反馈添加成功"}

# 文书润色相关

# 处理文书预约状态
@router.put("/document/status", response_model=dict)
def update_document_status(request: DocumentStatusUpdate, current_user: User = Depends(get_current_teacher), db: Session = Depends(get_db)):
    reservation = db.query(DocumentReservation).filter(
        DocumentReservation.id == request.reservation_id,
        DocumentReservation.teacher_id == current_user.id
    ).first()
    
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预约不存在"
        )
    
    if reservation.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该预约已处理"
        )
    
    reservation.status = request.status
    db.commit()
    
    return {"message": "状态更新成功"}

# 更新文书内容
@router.put("/document/content", response_model=dict)
def update_document_content(request: DocumentContentUpdate, current_user: User = Depends(get_current_teacher), db: Session = Depends(get_db)):
    reservation = db.query(DocumentReservation).filter(
        DocumentReservation.id == request.reservation_id,
        DocumentReservation.teacher_id == current_user.id
    ).first()
    
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预约不存在"
        )
    
    if reservation.status != "accepted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请先接受预约"
        )
    
    reservation.revised_content = request.revised_content
    db.commit()
    
    return {"message": "内容更新成功"}

# 更新文书进度
@router.put("/document/progress", response_model=dict)
def update_document_progress(request: DocumentProgressUpdate, current_user: User = Depends(get_current_teacher), db: Session = Depends(get_db)):
    reservation = db.query(DocumentReservation).filter(
        DocumentReservation.id == request.reservation_id,
        DocumentReservation.teacher_id == current_user.id
    ).first()
    
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预约不存在"
        )
    
    reservation.progress = request.progress
    
    # 如果进度为100%，自动标记为完成
    if request.progress == 100:
        reservation.status = "completed"
    
    db.commit()
    
    return {"message": "进度更新成功"}

# 学校管理相关

# 获取学校列表
@router.get("/school/list", response_model=List[dict])
def get_school_list(current_user: User = Depends(get_current_teacher), db: Session = Depends(get_db)):
    schools = db.query(School).all()
    
    return [
        {
            "id": school.id,
            "chinese_name": school.chinese_name,
            "english_name": school.english_name,
            "location": school.location,
            "rank": school.rank
        }
        for school in schools
    ]

# 添加学校
@router.post("/school/add", response_model=dict)
def add_school(request: SchoolAddRequest, current_user: User = Depends(get_current_teacher), db: Session = Depends(get_db)):
    # 检查学校是否已存在
    if db.query(School).filter(
        (School.chinese_name == request.chinese_name) |
        (School.english_name == request.english_name)
    ).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="学校已存在"
        )
    
    # 创建学校
    school = School(
        chinese_name=request.chinese_name,
        english_name=request.english_name,
        location=request.location,
        rank=request.rank,
        basic_info=request.basic_info,
        detailed_info=request.detailed_info
    )
    db.add(school)
    db.flush()  # 获取学校ID
    
    # 添加专业信息
    for major_data in request.majors:
        major = SchoolMajor(
            school_id=school.id,
            major_name=major_data["name"],
            major_rank=major_data.get("rank", 0)
        )
        db.add(major)
    
    db.commit()
    
    return {"message": "学校添加成功", "school_id": school.id}

# 更新学校信息
@router.put("/school/edit", response_model=dict)
def update_school(school_id: int, request: SchoolUpdateRequest, current_user: User = Depends(get_current_teacher), db: Session = Depends(get_db)):
    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学校不存在"
        )
    
    # 更新非空字段
    update_data = request.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(school, field, value)
    
    db.commit()
    
    return {"message": "学校信息更新成功"}

# 删除学校
@router.delete("/school/delete", response_model=dict)
def delete_school(school_id: int, current_user: User = Depends(get_current_teacher), db: Session = Depends(get_db)):
    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学校不存在"
        )
    
    db.delete(school)
    db.commit()
    
    return {"message": "学校删除成功"}