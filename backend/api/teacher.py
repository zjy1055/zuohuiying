from fastapi import APIRouter, Depends, HTTPException, status, Query, Body, Path
from sqlalchemy.orm import Session
from typing import List, Optional

from utils.database import get_db
from utils.dependencies import get_current_teacher
from models.database import User, TeacherProfile, School, SchoolMajor, TrainingReservation, DocumentReservation, StudentProfile, ReservationStatus
from pydantic import BaseModel, Field

router = APIRouter(prefix="/teacher", tags=["教师服务"])

# 数据模型
class TeacherProfileUpdate(BaseModel):
    """教师个人信息更新模型"""
    name: Optional[str] = Field(None, description="教师姓名")
    email: Optional[str] = Field(None, description="教师邮箱")
    phone: Optional[str] = Field(None, description="教师电话")
    subject: Optional[str] = Field(None, description="教授科目")

class TrainingStatusUpdate(BaseModel):
    """培训预约状态更新模型"""
    reservation_id: int = Field(..., description="预约ID")
    status: str = Field(..., description="状态：accepted(接受) 或 rejected(拒绝)")

class TrainingProgressUpdate(BaseModel):
    """培训进度更新模型"""
    reservation_id: int = Field(..., description="预约ID")
    attended_hours: int = Field(..., ge=0, description="已上课时长（小时）")

class TrainingFeedbackUpdate(BaseModel):
    """培训反馈更新模型"""
    reservation_id: int = Field(..., description="预约ID")
    feedback: str = Field(..., description="培训反馈内容")

class DocumentStatusUpdate(BaseModel):
    """文书预约状态更新模型"""
    reservation_id: int = Field(..., description="预约ID")
    status: str = Field(..., description="状态：accepted(接受) 或 rejected(拒绝)")

class DocumentContentUpdate(BaseModel):
    """文书内容更新模型"""
    reservation_id: int = Field(..., description="预约ID")
    revised_content: str = Field(..., description="修改后的文书内容")

class DocumentProgressUpdate(BaseModel):
    """文书进度更新模型"""
    reservation_id: int = Field(..., description="预约ID")
    progress: int = Field(..., ge=0, le=100, description="文书完成进度（0-100）")

class SchoolAddRequest(BaseModel):
    """添加学校请求模型"""
    chinese_name: str = Field(..., description="学校中文名")
    english_name: str = Field(..., description="学校英文名")
    location: str = Field(..., description="学校位置")
    ranking: int = Field(..., description="学校排名")
    introduction: str = Field("", description="学校简介")
    major_rankings: str = Field("", description="专业排名，格式：专业名称：排名；专业名称：排名")
    details: str = Field("", description="学校详细信息")

class SchoolUpdateRequest(BaseModel):
    """更新学校信息请求模型"""
    chinese_name: Optional[str] = Field(None, description="学校中文名")
    english_name: Optional[str] = Field(None, description="学校英文名")
    location: Optional[str] = Field(None, description="学校位置")
    ranking: Optional[int] = Field(None, description="学校排名")
    introduction: Optional[str] = Field(None, description="学校简介")
    major_rankings: Optional[str] = Field(None, description="专业排名，格式：专业名称：排名；专业名称：排名")
    details: Optional[str] = Field(None, description="学校详细信息")

# 获取个人信息
@router.get("/profile", response_model=dict, summary="获取教师个人信息", description="获取当前登录教师的个人基本信息")
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
@router.put("/profile", response_model=dict, summary="更新教师个人信息", description="更新当前登录教师的个人基本信息")
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
@router.get("/statistics/student", response_model=dict, summary="获取学生统计信息", description="获取教师相关的学生统计数据")
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

# 获取学生列表
@router.get("/students/list", response_model=dict, summary="获取学生列表", description="获取教师负责的学生列表，支持分页和搜索")
def get_students_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    # 构建查询
    query = db.query(StudentProfile).join(User)
    
    # 应用搜索条件
    if search:
        query = query.filter(
            (StudentProfile.name.like(f"%{search}%")) | 
            (User.email.like(f"%{search}%"))
        )
    
    # 计算总数
    total_count = query.count()
    total_pages = (total_count + page_size - 1) // page_size
    
    # 分页查询
    offset = (page - 1) * page_size
    students = query.offset(offset).limit(page_size).all()
    
    # 构建响应
    return {
        "students": [
            {
                "id": student.user_id,
                "name": student.name,
                "gender": student.gender,
                "toefl": student.toefl,
                "gre": student.gre,
                "gpa": student.gpa,
                "target_region": student.target_region
            }
            for student in students
        ],
        "total_pages": total_pages,
        "current_page": page,
        "total_count": total_count
    }

# 留学成功率预测
@router.get("/statistics/predict", response_model=dict, summary="预测留学成功率", description="根据学生信息预测申请指定学校的成功率")
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
@router.get("/document/list", response_model=List[dict], summary="获取文书预约列表", description="获取所有文书预约列表，支持分页和状态筛选")
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

@router.get("/document/detail", response_model=dict, summary="获取文书预约详情", description="获取指定文书预约的详细信息")
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

@router.get("/training/list", response_model=List[dict], summary="获取培训预约列表", description="获取所有培训预约列表，支持分页和状态筛选")
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
@router.get("/training/detail", response_model=dict, summary="获取培训预约详情", description="获取指定培训预约的详细信息")
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
@router.put("/training/status", response_model=dict, summary="更新培训预约状态", description="更新指定培训预约的状态（接受或拒绝）")
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
    
    if reservation.status != ReservationStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该预约已处理"
        )
    
    try:
        # 验证状态值是否有效
        if request.status not in [status.value for status in ReservationStatus]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的状态值"
            )
        reservation.status = ReservationStatus(request.status)
        db.commit()
        
        return {"message": "状态更新成功"}
    except HTTPException:
        # 重新抛出已定义的HTTPException
        raise
    except Exception as e:
        db.rollback()
        # 记录详细错误信息
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"预约状态更新失败: {str(e)}", exc_info=True)
        # 返回通用错误消息，不泄露敏感信息
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新失败，请稍后重试"
        )

# 更新培训进度
@router.put("/training/progress", response_model=dict, summary="更新培训进度", description="更新培训已上课时长")
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
    
    if reservation.status != ReservationStatus.ACCEPTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请先接受预约"
        )
    
    if request.attended_hours > reservation.total_hours:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已上课时不能超过总课时"
        )
    
    try:
        reservation.attended_hours = request.attended_hours
        
        # 如果已上完所有课时，自动标记为完成
        if request.attended_hours == reservation.total_hours:
            reservation.status = ReservationStatus.COMPLETED
        
        db.commit()
        
        return {"message": "进度更新成功"}
    except Exception as e:
        db.rollback()
        # 记录详细错误信息
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"培训进度更新失败: {str(e)}", exc_info=True)
        # 返回通用错误消息，不泄露敏感信息
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新失败，请稍后重试"
        )

# 添加培训反馈
@router.put("/training/feedback", response_model=dict, summary="添加培训反馈", description="为指定培训预约添加反馈评价")
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
    
    try:
        reservation.feedback = request.feedback
        db.commit()
        
        return {"message": "反馈添加成功"}
    except Exception as e:
        db.rollback()
        # 记录详细错误信息
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"培训反馈更新失败: {str(e)}", exc_info=True)
        # 返回通用错误消息，不泄露敏感信息
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新失败，请稍后重试"
        )

# 文书润色相关

# 处理文书预约状态
@router.put("/document/status", response_model=dict, summary="更新文书预约状态", description="更新指定文书预约的状态（接受或拒绝）")
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
    
    if reservation.status != ReservationStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该预约已处理"
        )
    
    try:
        # 验证状态值是否有效
        if request.status not in [status.value for status in ReservationStatus]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的状态值"
            )
        reservation.status = ReservationStatus(request.status)
        db.commit()
        
        return {"message": "状态更新成功"}
    except HTTPException:
        # 重新抛出已定义的HTTPException
        raise
    except Exception as e:
        db.rollback()
        # 记录详细错误信息
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"文书预约状态更新失败: {str(e)}", exc_info=True)
        # 返回通用错误消息，不泄露敏感信息
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新失败，请稍后重试"
        )

# 更新文书内容
@router.put("/document/content", response_model=dict, summary="更新文书内容", description="更新文书修改后的内容")
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
    
    if reservation.status != ReservationStatus.ACCEPTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请先接受预约"
        )
    
    try:
        reservation.revised_content = request.revised_content
        db.commit()
        
        return {"message": "内容更新成功"}
    except Exception as e:
        db.rollback()
        # 记录详细错误信息
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"文书内容更新失败: {str(e)}", exc_info=True)
        # 返回通用错误消息，不泄露敏感信息
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新失败，请稍后重试"
        )

# 更新文书进度
@router.put("/document/progress", response_model=dict, summary="更新文书进度", description="更新文书完成进度（0-100）")
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
    
    try:
        reservation.progress = request.progress
        
        # 如果进度为100%，自动标记为完成
        if request.progress == 100:
            reservation.status = ReservationStatus.COMPLETED
        
        db.commit()
        
        return {"message": "进度更新成功"}
    except Exception as e:
        db.rollback()
        # 记录详细错误信息
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"文书进度更新失败: {str(e)}", exc_info=True)
        # 返回通用错误消息，不泄露敏感信息
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新失败，请稍后重试"
        )

# 学校管理相关

# 获取学校详情
@router.get("/school/detail", response_model=dict, summary="获取学校详情", description="获取指定学校的详细信息，包括专业排名")
def get_school_detail(
    school_id: int = Query(..., description="学校ID"),
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    # 查找学校
    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学校不存在"
        )
    
    # 获取学校的专业排名
    majors = db.query(SchoolMajor).filter(SchoolMajor.school_id == school_id).all()
    major_rankings_str = "；".join([f"{major.major_name}：{major.major_rank}" for major in majors])
    
    # 返回详情
    return {
        "id": school.id,
        "chinese_name": school.chinese_name,
        "english_name": school.english_name,
        "location": school.location,
        "ranking": school.ranking,
        "introduction": school.introduction,
        "details": school.details,
        "major_rankings": major_rankings_str
    }

# 获取学校列表
@router.get("/school/list", response_model=dict, summary="获取学校列表", description="分页获取学校列表，支持搜索功能")
def get_school_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    current_user: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    # 构建查询
    query = db.query(School)
    
    # 应用搜索条件
    if search:
        query = query.filter(
            (School.chinese_name.like(f"%{search}%")) | 
            (School.english_name.like(f"%{search}%")) |
            (School.location.like(f"%{search}%"))
        )
    
    # 计算总数
    total_count = query.count()
    total_pages = (total_count + page_size - 1) // page_size
    
    # 分页查询
    offset = (page - 1) * page_size
    schools = query.offset(offset).limit(page_size).all()
    
    # 构建响应
    return {
        "schools": [
            {
                "id": school.id,
                "chinese_name": school.chinese_name,
                "english_name": school.english_name,
                "location": school.location,
                "ranking": school.ranking
            }
            for school in schools
        ],
        "total_pages": total_pages,
        "current_page": page,
        "total_count": total_count
    }

# 添加学校
@router.post("/school/add", response_model=dict, summary="添加新学校", description="添加新的学校信息，包括学校基本信息和专业排名")
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
        ranking=request.ranking,
        introduction=request.introduction,
        details=request.details
    )
    db.add(school)
    db.flush()  # 获取学校ID
    
    # 处理专业排名信息
    if request.major_rankings:
        # 解析专业排名字符串，格式如："计算机：10；商科：20；工程：15"
        major_pairs = request.major_rankings.split("；")
        for pair in major_pairs:
            if "：" in pair:
                try:
                    major_name, major_rank_str = pair.split("：")
                    major_rank = int(major_rank_str.strip())
                    major = SchoolMajor(
                        school_id=school.id,
                        major_name=major_name.strip(),
                        major_rank=major_rank
                    )
                    db.add(major)
                except (ValueError, IndexError):
                    # 跳过无效格式的专业排名
                    continue
    
    db.commit()
    
    return {"message": "学校添加成功", "school_id": school.id}

# 更新学校信息
@router.put("/school/edit/{school_id}", response_model=dict, summary="更新学校信息", description="更新指定学校的信息，包括基本信息和专业排名")
def update_school(school_id: int = Path(..., description="学校ID"), request: SchoolUpdateRequest = Body(...), current_user: User = Depends(get_current_teacher), db: Session = Depends(get_db)):
    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学校不存在"
        )
    
    # 更新字段
    update_data = request.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(school, field, value)
    
    # 处理专业排名
    if 'major_rankings' in update_data:
        major_rankings = update_data['major_rankings']
        # 清除现有专业排名
        db.query(SchoolMajor).filter(SchoolMajor.school_id == school_id).delete()
        # 添加新的专业排名
        if major_rankings:
            major_pairs = major_rankings.split("；")
            for pair in major_pairs:
                if "：" in pair:
                    try:
                        major_name, major_rank_str = pair.split("：")
                        major_rank = int(major_rank_str.strip())
                        major = SchoolMajor(
                            school_id=school.id,
                            major_name=major_name.strip(),
                            major_rank=major_rank
                        )
                        db.add(major)
                    except (ValueError, IndexError):
                        # 跳过无效格式的专业排名
                        continue
    
    db.commit()
    
    return {"message": "学校信息更新成功"}

# 删除学校
@router.delete("/school/delete", response_model=dict, summary="删除学校", description="删除指定的学校信息")
def delete_school(school_id: int = Query(..., description="学校ID"), current_user: User = Depends(get_current_teacher), db: Session = Depends(get_db)):
    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学校不存在"
        )
    
    db.delete(school)
    db.commit()
    
    return {"message": "学校删除成功"}