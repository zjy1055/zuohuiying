from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime

from models.database import School, SchoolMajor
from utils.dependencies import get_db

router = APIRouter()

# Pydantic 模型用于数据验证
class SchoolBase(BaseModel):
    chinese_name: str = Field(..., min_length=1, max_length=100, description="学校中文名称")
    english_name: str = Field(..., min_length=1, max_length=200, description="学校英文名称")
    location: str = Field(..., min_length=1, max_length=100, description="学校所在地")
    ranking: int = Field(..., gt=0, description="学校排名")
    introduction: Optional[str] = Field(None, description="学校介绍")
    details: Optional[str] = Field(None, description="学校详细信息")

class SchoolCreate(SchoolBase):
    pass

class SchoolUpdate(BaseModel):
    chinese_name: Optional[str] = Field(None, min_length=1, max_length=100, description="学校中文名称")
    english_name: Optional[str] = Field(None, min_length=1, max_length=200, description="学校英文名称")
    location: Optional[str] = Field(None, min_length=1, max_length=100, description="学校所在地")
    ranking: Optional[int] = Field(None, gt=0, description="学校排名")
    introduction: Optional[str] = Field(None, description="学校介绍")
    details: Optional[str] = Field(None, description="学校详细信息")

class SchoolResponse(BaseModel):
    id: int
    chinese_name: str
    english_name: str
    location: str
    ranking: int
    introduction: Optional[str]
    details: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

@router.get("/schools", response_model=List[SchoolResponse])
def get_schools(db: Session = Depends(get_db)):
    """
    获取所有学校列表
    """
    try:
        schools = db.query(School).all()
        return schools
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取学校列表失败: {str(e)}")

@router.get("/schools/{school_id}", response_model=SchoolResponse)
def get_school_detail(school_id: int, db: Session = Depends(get_db)):
    """
    获取单个学校的详细信息
    """
    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="学校不存在")
    return school

@router.post("/schools", response_model=SchoolResponse)
def create_school(school_data: SchoolCreate, db: Session = Depends(get_db)):
    """
    添加新学校
    """
    try:
        # 检查学校是否已存在
        existing_school = db.query(School).filter(
            (School.chinese_name == school_data.chinese_name) |
            (School.english_name == school_data.english_name)
        ).first()
        
        if existing_school:
            raise HTTPException(status_code=400, detail="学校已存在")
        
        # 创建新学校
        new_school = School(**school_data.dict())
        db.add(new_school)
        db.commit()
        db.refresh(new_school)
        
        return new_school
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建学校失败: {str(e)}")

@router.put("/schools/{school_id}", response_model=SchoolResponse)
def update_school(school_id: int, school_data: SchoolUpdate, db: Session = Depends(get_db)):
    """
    更新学校信息
    """
    try:
        # 查找学校
        school = db.query(School).filter(School.id == school_id).first()
        if not school:
            raise HTTPException(status_code=404, detail="学校不存在")
        
        # 检查名称是否与其他学校冲突
        if school_data.chinese_name and school_data.chinese_name != school.chinese_name:
            existing = db.query(School).filter(School.chinese_name == school_data.chinese_name).first()
            if existing:
                raise HTTPException(status_code=400, detail="中文名称已存在")
        
        if school_data.english_name and school_data.english_name != school.english_name:
            existing = db.query(School).filter(School.english_name == school_data.english_name).first()
            if existing:
                raise HTTPException(status_code=400, detail="英文名称已存在")
        
        # 更新学校信息
        update_data = school_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(school, field, value)
        
        school.updated_at = datetime.now()
        db.commit()
        db.refresh(school)
        
        return school
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新学校失败: {str(e)}")

@router.delete("/schools/{school_id}", response_model=dict)
def delete_school(school_id: int, db: Session = Depends(get_db)):
    """
    删除学校
    """
    try:
        # 查找学校
        school = db.query(School).filter(School.id == school_id).first()
        if not school:
            raise HTTPException(status_code=404, detail="学校不存在")
        
        # 删除学校（会级联删除相关的专业排名）
        db.delete(school)
        db.commit()
        
        return {"message": "学校删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除学校失败: {str(e)}")