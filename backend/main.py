from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from contextlib import asynccontextmanager
import logging

from utils.config import settings
from utils.database import create_tables
from api import auth, student, teacher, schools

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


# 配置CORS，确保正确允许前端跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 明确指定前端源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # 暴露所有响应头
)

# 注册路由
app.include_router(auth.router)
app.include_router(student.router)
app.include_router(teacher.router)
app.include_router(schools.router, prefix="/api")

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

# 全局异常处理器 - 处理数据库错误
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    # 记录详细错误信息到日志，但不返回给客户端
    logger.error(f"数据库错误: {str(exc)}", exc_info=True)
    # 向客户端返回通用错误消息
    return JSONResponse(
        status_code=500,
        content={
            "error": "内部服务器错误",
            "detail": "数据库操作失败，请稍后重试",
            "code": "DATABASE_ERROR"
        }
    )

# 全局异常处理器 - 处理请求验证错误
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # 格式化验证错误消息
    detail = []
    for error in exc.errors():
        field = '.'.join(str(loc) for loc in error['loc']) if error['loc'] else 'body'
        detail.append({
            "field": field,
            "message": error['msg'],
            "type": error['type']
        })
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "请求验证失败",
            "detail": detail,
            "code": "VALIDATION_ERROR"
        }
    )

# 全局异常处理器 - 处理所有其他未捕获的异常
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # 记录详细错误信息到日志，但不返回给客户端
    logger.error(f"未处理的异常: {str(exc)}", exc_info=True)
    # 向客户端返回通用错误消息
    return JSONResponse(
        status_code=500,
        content={
            "error": "内部服务器错误",
            "detail": "服务器暂时无法处理请求，请稍后重试",
            "code": "INTERNAL_ERROR"
        }
    )