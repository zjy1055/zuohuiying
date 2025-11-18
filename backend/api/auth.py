from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from utils.database import get_db
from utils.security import verify_password, get_password_hash, create_access_token
from utils.config import settings

from models.database import User, StudentProfile, TeacherProfile
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/auth", tags=["认证"])

# 请求模型
class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str  # student 或 teacher
    # 基础信息
    name: str
    email: EmailStr
    phone: str
    # 留学生特有信息
    toefl: float = None
    gre: float = None
    gpa: float = None
    target_region: str = None
    gender: str = None
    age: int = None
    # 教师特有信息
    subject: str = None

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    role: str

# 注册接口
@router.post("/register", response_model=dict)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    # 验证用户名是否已存在
    if db.query(User).filter(User.username == request.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 验证角色
    if request.role not in ["student", "teacher"]:
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

# 登录接口
@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 解析表单数据，获取角色信息
    # OAuth2PasswordRequestForm不包含role字段，我们从scope中获取
    role = "student"  # 默认角色
    if form_data.scopes:
        role = form_data.scopes[0] if form_data.scopes[0] in ["student", "teacher"] else "student"
    
    # 查找用户
    user = db.query(User).filter(User.username == form_data.username).first()
    
    # 验证用户和密码
    if not user or not verify_password(form_data.password, user.password) or user.role != role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名、密码或角色错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "role": user.role
    }