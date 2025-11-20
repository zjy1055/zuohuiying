from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional

from utils.database import get_db
from utils.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from utils.config import settings
from utils.dependencies import get_current_user_from_refresh
from models.database import UserRole

from models.database import User, StudentProfile, TeacherProfile
from pydantic import BaseModel, EmailStr, Field

router = APIRouter(prefix="/auth", tags=["认证"])

# 请求模型
class RegisterRequest(BaseModel):
    """用户注册请求模型"""
    username: str = Field(..., description="用户名，用于登录，必须唯一", example="student001")
    password: str = Field(..., description="密码，用于登录验证", example="SecurePass123")
    role: str = Field(..., description="用户角色，必须是 'student' 或 'teacher'", example="student")
    # 基础信息
    name: str = Field(..., description="真实姓名", example="张三")
    email: EmailStr = Field(..., description="电子邮箱，用于联系", example="zhangsan@example.com")
    phone: str = Field(..., description="手机号码，用于联系", example="13800138000")
    # 留学生特有信息
    toefl: Optional[float] = Field(None, description="托福成绩，0-120分", example=105.0, ge=0, le=120)
    gre: Optional[float] = Field(None, description="GRE成绩，260-340分", example=320.0, ge=260, le=340)
    gpa: Optional[float] = Field(None, description="GPA成绩，0.0-4.0分", example=3.5, ge=0, le=4.0)
    target_region: Optional[str] = Field(None, description="目标留学地区", example="美国")
    gender: Optional[str] = Field(None, description="性别", example="男")
    age: Optional[int] = Field(None, description="年龄，18-100岁", example=22, ge=18, le=100)
    # 教师特有信息
    subject: Optional[str] = Field(None, description="教师擅长科目", example="英语")

class Token(BaseModel):
    """登录成功后的令牌响应模型"""
    access_token: str = Field(..., description="访问令牌，用于后续API请求的身份验证")
    refresh_token: str = Field(..., description="刷新令牌，用于获取新的访问令牌")
    token_type: str = Field(..., description="令牌类型，通常为 'bearer'")
    user_id: int = Field(..., description="用户ID")
    role: str = Field(..., description="用户角色")

# 注册接口
@router.post("/register", response_model=dict, summary="用户注册", description="创建新用户账号，同时创建对应的学生或教师信息")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    # 验证用户名是否已存在
    if db.query(User).filter(User.username == request.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 验证角色
    if request.role not in [UserRole.STUDENT.value, UserRole.TEACHER.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色必须是 student 或 teacher"
        )
    
    # 创建用户
    hashed_password = get_password_hash(request.password)
    user = User(
        username=request.username,
        password=hashed_password,
        role=request.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 创建对应的用户信息
    if request.role == "student":
        student_profile = StudentProfile(
            user_id=user.id,
            name=request.name,
            gender=request.gender,
            age=request.age,
            toefl=request.toefl,
            gre=request.gre,
            gpa=request.gpa,
            target_region=request.target_region,
            email=request.email,
            phone=request.phone
        )
        db.add(student_profile)
    else:
        teacher_profile = TeacherProfile(
            user_id=user.id,
            name=request.name,
            email=request.email,
            phone=request.phone,
            subject=request.subject
        )
        db.add(teacher_profile)
    
    db.commit()
    
    return {"message": "注册成功", "user_id": user.id}

# 登录请求模型
class LoginRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    role: str = Field(default="student", description="用户角色，student或teacher")

# 登录接口 - 简化版本，支持JSON和表单格式
@router.post("/login", response_model=Token, summary="用户登录", description="验证用户凭据并返回访问令牌")
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    try:
        # 从请求模型获取参数
        username = request.username
        password = request.password
        role = request.role
        
        # 验证必要参数
        if not username or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名和密码不能为空"
            )
        
        # 查找用户
        user = db.query(User).filter(User.username == username).first()
        
        # 验证用户和密码
        if not user or not verify_password(password, user.password) or user.role != role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名、密码或角色错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 创建访问令牌和刷新令牌
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role},
            expires_delta=access_token_expires
        )
        
        # 创建刷新令牌（有效期7天）
        refresh_token_expires = timedelta(days=7)
        refresh_token = create_refresh_token(
            data={"sub": user.username, "role": user.role},
            expires_delta=refresh_token_expires
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user_id": user.id,
            "role": user.role
        }
    except HTTPException:
        # 重新抛出已定义的HTTP异常
        raise
    except Exception as e:
        # 捕获其他所有异常并返回500错误
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器内部错误: {str(e)}"
        ) from e

# 刷新访问令牌
@router.post("/refresh", response_model=dict, summary="刷新访问令牌", description="使用刷新令牌获取新的访问令牌")
def refresh_token(current_user: User = Depends(get_current_user_from_refresh)):
    # 创建新的访问令牌
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": current_user.username, "role": current_user.role},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": current_user.id,
        "role": current_user.role
    }
    