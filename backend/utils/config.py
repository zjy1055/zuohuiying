from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """应用配置类"""
    # 应用基本配置
    app_name: str = "Study Abroad Service Platform"
    debug: bool = True
    
    # 数据库配置
    database_url: str = "sqlite:///./study_abroad.db"
    
    # JWT配置
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24小时
    

    
    class Config:
        env_file = ".env"
        case_sensitive = False

# 创建全局配置实例
settings = Settings()