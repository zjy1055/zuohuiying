from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum, CheckConstraint
import enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import time

# 使用 timezone-aware 本地时间（去掉 tzinfo 以兼容 SQLite）
def get_local_time():
    return datetime.now().replace(tzinfo=None)  # SQLite 不支持 tzinfo，需去掉

Base = declarative_base()

# 用户表
# 定义枚举类型
class UserRole(str, enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"

class ReservationStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    COMPLETED = "completed"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)  # 使用枚举约束
    created_at = Column(DateTime, default=get_local_time)
    updated_at = Column(DateTime, default=get_local_time, onupdate=get_local_time)
    
    # 关联关系
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    teacher_profile = relationship("TeacherProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    student_training_reservations = relationship("TrainingReservation", back_populates="student", foreign_keys="TrainingReservation.student_id")
    teacher_training_reservations = relationship("TrainingReservation", back_populates="teacher", foreign_keys="TrainingReservation.teacher_id")
    student_document_reservations = relationship("DocumentReservation", back_populates="student", foreign_keys="DocumentReservation.student_id")
    teacher_document_reservations = relationship("DocumentReservation", back_populates="teacher", foreign_keys="DocumentReservation.teacher_id")

# 留学生信息表
class StudentProfile(Base):
    __tablename__ = "student_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(50), nullable=False)
    gender = Column(String(10))
    age = Column(Integer)
    toefl = Column(Float)
    gre = Column(Float)
    gpa = Column(Float)
    
    # 添加数据约束
    __table_args__ = (
        CheckConstraint('age >= 18 AND age <= 100', name='check_valid_age'),
        CheckConstraint('toefl >= 0 AND toefl <= 120', name='check_valid_toefl'),
        CheckConstraint('gre >= 260 AND gre <= 340', name='check_valid_gre'),
        CheckConstraint('gpa >= 0 AND gpa <= 4.0', name='check_valid_gpa'),
    )
    target_region = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    created_at = Column(DateTime, default=get_local_time)
    updated_at = Column(DateTime, default=get_local_time, onupdate=get_local_time)
    
    # 关联关系
    user = relationship("User", back_populates="student_profile")

# 教师信息表
class TeacherProfile(Base):
    __tablename__ = "teacher_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(50), nullable=False)
    email = Column(String(100))
    phone = Column(String(20))
    subject = Column(String(100))  # 擅长科目
    created_at = Column(DateTime, default=get_local_time)
    updated_at = Column(DateTime, default=get_local_time, onupdate=get_local_time)
    
    # 关联关系
    user = relationship("User", back_populates="teacher_profile")

# 学校表
class School(Base):
    __tablename__ = "schools"
    
    id = Column(Integer, primary_key=True, index=True)
    chinese_name = Column(String(100), unique=True, nullable=False)
    english_name = Column(String(200), unique=True, nullable=False)
    location = Column(String(100))
    ranking = Column(Integer)
    
    # 添加排名约束
    __table_args__ = (
        CheckConstraint('ranking > 0', name='check_valid_school_rank'),
    )
    introduction = Column(Text)
    details = Column(Text)
    created_at = Column(DateTime, default=get_local_time)
    updated_at = Column(DateTime, default=get_local_time, onupdate=get_local_time)
    
    # 关联关系
    majors = relationship("SchoolMajor", back_populates="school", cascade="all, delete-orphan")

# 学校专业排名表
class SchoolMajor(Base):
    __tablename__ = "school_majors"
    
    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    major_name = Column(String(100), nullable=False)
    major_rank = Column(Integer)
    
    # 添加排名约束
    __table_args__ = (
        CheckConstraint('major_rank > 0', name='check_valid_major_rank'),
    )
    created_at = Column(DateTime, default=get_local_time)
    updated_at = Column(DateTime, default=get_local_time, onupdate=get_local_time)
    
    # 关联关系
    school = relationship("School", back_populates="majors")

# 语言培训预约表
class TrainingReservation(Base):
    __tablename__ = "training_reservations"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    total_hours = Column(Integer, nullable=False)
    training_type = Column(String(50))
    notes = Column(Text)
    status = Column(Enum(ReservationStatus), default=ReservationStatus.PENDING)
    attended_hours = Column(Integer, default=0)
    feedback = Column(Text)
    homework = Column(Text)
    
    # 添加小时数约束
    __table_args__ = (
        CheckConstraint('total_hours > 0', name='check_valid_total_hours'),
        CheckConstraint('attended_hours >= 0', name='check_valid_attended_hours'),
    )
    created_at = Column(DateTime, default=get_local_time)
    updated_at = Column(DateTime, default=get_local_time, onupdate=get_local_time)
    
    # 关联关系
    student = relationship("User", back_populates="student_training_reservations", foreign_keys=[student_id])
    teacher = relationship("User", back_populates="teacher_training_reservations", foreign_keys=[teacher_id])

# 文书润色预约表
class DocumentReservation(Base):
    __tablename__ = "document_reservations"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    document_count = Column(Integer, nullable=False)
    document_type = Column(String(50))
    target_school = Column(String(200))
    notes = Column(Text)
    comments = Column(Text)
    status = Column(Enum(ReservationStatus), default=ReservationStatus.PENDING)
    progress = Column(Integer, default=0)  # 0-100%
    
    # 添加文档数量和进度约束
    __table_args__ = (
        CheckConstraint('document_count > 0', name='check_valid_document_count'),
        CheckConstraint('progress >= 0 AND progress <= 100', name='check_valid_progress'),
    )
    original_content = Column(Text)
    revised_content = Column(Text)
    file_path = Column(String(255))
    created_at = Column(DateTime, default=get_local_time)
    updated_at = Column(DateTime, default=get_local_time, onupdate=get_local_time)
    
    # 关联关系
    student = relationship("User", back_populates="student_document_reservations", foreign_keys=[student_id])
    teacher = relationship("User", back_populates="teacher_document_reservations", foreign_keys=[teacher_id])

# 成功案例表
class SuccessCase(Base):
    __tablename__ = "success_cases"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    file_path = Column(String(255))
    created_at = Column(DateTime, default=get_local_time)
    updated_at = Column(DateTime, default=get_local_time, onupdate=get_local_time)

# 创建数据库会话
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 导入配置
from utils.config import settings

# 创建数据库引擎，启用SQLite外键约束
engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})

# 启用外键约束
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)