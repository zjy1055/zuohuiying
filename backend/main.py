from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from utils.config import settings
from utils.database import create_tables
from api import auth, student, teacher

# 应用启动和关闭事件
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时创建数据库表
    create_tables()
    print("数据库表创建完成")
    yield
    # 关闭时的清理工作
    pass

# 创建FastAPI应用实例
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="留学服务平台后端API",
    lifespan=lifespan
)


# 配置基本CORS，允许本地访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源（适合开发环境）
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(student.router)
app.include_router(teacher.router)

# 根路径
@app.get("/")
def root():
    return {
        "message": "留学服务平台后端API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# 健康检查
@app.get("/health")
def health_check():
    return {"status": "healthy"}