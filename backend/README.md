# 留学服务平台后端系统

## 项目概述

本项目是留学服务平台的后端系统，基于FastAPI框架开发，提供用户认证、留学生服务、教师服务和学校信息等功能的API接口。系统支持留学生进行个人信息管理、学校查询、培训预约和文书润色预约等操作，同时为教师提供相应的服务管理功能。

## 技术栈

- **框架**: FastAPI 0.95.0
- **数据库**: SQLite (通过SQLAlchemy ORM)
- **认证**: JWT (JSON Web Token)
- **密码加密**: bcrypt
- **API文档**: Swagger UI (自动生成)
- **运行环境**: Uvicorn 0.22.0
- **配置管理**: python-dotenv

## 环境要求

- Python 3.8+
- pip 20.0+
- SQLite (Python标准库内置，无需单独安装)

## 项目结构

```
backend/
├── api/                  # API路由模块
│   ├── auth.py           # 认证相关接口
│   ├── student.py        # 留学生服务接口
│   ├── teacher.py        # 教师服务接口
│   └── schools.py        # 学校信息接口
├── models/               # 数据模型
│   └── database.py       # 数据库模型定义
├── utils/                # 工具函数
│   ├── config.py         # 配置管理
│   ├── database.py       # 数据库连接和会话管理
│   ├── dependencies.py   # 依赖项（如获取当前用户）
│   └── security.py       # 安全相关功能（密码加密、JWT生成等）
├── .env                  # 环境变量配置
├── db.py                 # SQLite数据库可视化工具
├── main.py               # 应用入口
├── requirements.txt      # 项目依赖
└── test_api.py           # API测试脚本
```

## 安装步骤

### 1. 安装Python（如需）

如果您的系统上尚未安装Python，可以使用以下方法安装（以Windows为例）：

```powershell
# 使用winget安装Python（Windows 10/11）
winget install --id Python.Python.3.11

# 或者从官网下载安装包：https://www.python.org/downloads/
```

安装完成后，验证Python版本：

```powershell
python --version
# 或
python3 --version
```

### 2. 克隆项目（如果尚未克隆）

```powershell
cd d:\zuohuiying-main
```

### 3. 创建虚拟环境（推荐）

```powershell
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境（Windows）
venv\Scripts\activate

# 激活虚拟环境（macOS/Linux）
# source venv/bin/activate
```

### 4. 安装依赖

```powershell
# 进入后端目录
cd backend

# 安装项目依赖
pip install -r requirements.txt
```

### 5. 配置环境变量

确保`.env`文件存在并包含必要的配置：

```
# .env 文件内容
SECRET_KEY=your_secret_key_here
```

您可以生成一个随机的SECRET_KEY：

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 运行项目

### 启动后端服务

```powershell
# 确保在backend目录下且虚拟环境已激活
uvicorn main:app --reload
```

服务启动后，您可以访问以下地址：

- API文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health
- 根路径：http://localhost:8000/

## 数据库说明

### 数据模型

系统包含以下主要数据模型：

1. **User** - 用户表，存储基本认证信息
2. **StudentProfile** - 留学生信息表
3. **TeacherProfile** - 教师信息表
4. **School** - 学校表
5. **SchoolMajor** - 学校专业排名表
6. **TrainingReservation** - 语言培训预约表
7.  **SuccessCase** - 成功案例表

### 数据库初始化

应用启动时会自动创建所需的数据库表。数据库文件为`study_abroad.db`，位于项目根目录。

### 数据库可视化工具

项目包含一个简单的SQLite可视化工具（`db.py`），可以运行它来查看和管理数据库内容：

```powershell
python db.py
```
情

## 安全配置

### CORS配置

系统已配置CORS，允许来自前端（http://localhost:5173）的跨域请求。如需修改，请在`main.py`中更新：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 可修改为生产环境域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
```

### 错误处理

系统实现了全局异常处理器，对数据库错误、请求验证错误和其他未捕获的异常进行统一处理，返回友好的错误信息。

## 测试

项目包含API测试脚本（`test_api.py`），可以运行它来测试API功能：

```powershell
python test_api.py
```

## 部署说明

### 生产环境部署

1. 创建生产环境配置文件（`.env.production`）
2. 设置`debug=False`
3. 使用生产级WSGI服务器（如Gunicorn）
4. 配置HTTPS

示例命令：

```bash
# 使用Gunicorn部署
pip install gunicorn
GUNICORN_CMD_ARGS="--workers=4 --bind=0.0.0.0:8000" gunicorn "main:app"
```

## 注意事项

1. 生产环境中请使用强密码和安全的SECRET_KEY
2. 定期备份数据库
3. 根据需要调整CORS配置
4. 监控系统日志以捕获潜在问题

