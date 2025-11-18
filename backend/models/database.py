from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# 用户表
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # student 或 teacher
    created_at = Column(DateTime, default=datetime.utcnow)
    
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
    target_region = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    
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
    
    # 关联关系
    user = relationship("User", back_populates="teacher_profile")

# 学校表
class School(Base):
    __tablename__ = "schools"
    
    id = Column(Integer, primary_key=True, index=True)
    chinese_name = Column(String(100), unique=True, nullable=False)
    english_name = Column(String(200), unique=True, nullable=False)
    location = Column(String(100))
    rank = Column(Integer)
    basic_info = Column(Text)
    detailed_info = Column(Text)
    
    # 关联关系
    majors = relationship("SchoolMajor", back_populates="school", cascade="all, delete-orphan")

# 学校专业排名表
class SchoolMajor(Base):
    __tablename__ = "school_majors"
    
    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    major_name = Column(String(100), nullable=False)
    major_rank = Column(Integer)
    
    # 关联关系
    school = relationship("School", back_populates="majors")

# 语言培训预约表
class TrainingReservation(Base):
    __tablename__ = "training_reservations"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_hours = Column(Integer, nullable=False)
    training_type = Column(String(50))
    notes = Column(Text)
    status = Column(String(20), default="pending")  # pending, accepted, completed
    attended_hours = Column(Integer, default=0)
    feedback = Column(Text)
    homework = Column(Text)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
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
    status = Column(String(20), default="pending")  # pending, accepted, completed
    progress = Column(Integer, default=0)  # 0-100%
    original_content = Column(Text)
    revised_content = Column(Text)
    file_path = Column(String(255))
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
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
    created_at = Column(DateTime, default=datetime.utcnow)