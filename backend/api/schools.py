from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from models.database import School, SessionLocal
from utils.dependencies import get_db

router = APIRouter()

@router.get("/schools", response_model=List[dict])
def get_schools(db: Session = Depends(get_db)):
    """
    获取所有学校列表
    """
    try:
        schools = db.query(School).all()
        
        # 转换为字典列表返回
        return [
            {
                "id": school.id,
                "chinese_name": school.chinese_name,
                "english_name": school.english_name,
                "location": school.location,
                "ranking": school.ranking,
                "introduction": school.introduction
            }
            for school in schools
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取学校列表失败: {str(e)}")

@router.get("/schools/{school_id}", response_model=dict)
def get_school_detail(school_id: int, db: Session = Depends(get_db)):
    """
    获取单个学校的详细信息
    """
    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="学校不存在")
    
    return {
        "id": school.id,
        "chinese_name": school.chinese_name,
        "english_name": school.english_name,
        "location": school.location,
        "ranking": school.ranking,
        "introduction": school.introduction,
        "details": school.details
    }