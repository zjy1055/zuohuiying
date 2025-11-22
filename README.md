# 留学服务平台技术文档

## 1. 项目概述

留学服务平台是一个为留学生和留学顾问教师提供全方位服务的Web应用系统。该系统旨在帮助学生找到合适的留学目标院校，预约语言培训和文书润色服务，同时为教师提供学生管理、培训预约处理和留学成功率预测等功能。

主要功能包括：

- 用户认证与授权（学生/教师双角色系统）
- 个人信息管理
- 学校搜索与推荐
- 语言培训预约
- 教师管理功能
- 留学成功率预测
- 成功案例展示

## 2. 技术栈

### 2.1 后端技术栈

| 技术/框架  | 版本   | 用途         | 来源                                                                                                      |
| ---------- | ------ | ------------ | --------------------------------------------------------------------------------------------------------- |
| Python     | 3.7+   | 主要开发语言 | `<mcfile name="requirements.txt" path="d:\graduate\zuohuiying-main\backend\requirements.txt"></mcfile>` |
| FastAPI    | 0.95.0 | Web框架      | `<mcfile name="requirements.txt" path="d:\graduate\zuohuiying-main\backend\requirements.txt"></mcfile>` |
| Uvicorn    | 0.22.0 | ASGI服务器   | `<mcfile name="requirements.txt" path="d:\graduate\zuohuiying-main\backend\requirements.txt"></mcfile>` |
| SQLAlchemy | 2.0.10 | ORM框架      | `<mcfile name="requirements.txt" path="d:\graduate\zuohuiying-main\backend\requirements.txt"></mcfile>` |
| SQLite     | -      | 数据库       | `<mcfile name="database.py" path="d:\graduate\zuohuiying-main\backend\models\database.py"></mcfile>`    |
| Pydantic   | 1.10.7 | 数据验证     | `<mcfile name="requirements.txt" path="d:\graduate\zuohuiying-main\backend\requirements.txt"></mcfile>` |
| JWT        | 3.3.0  | 身份认证     | `<mcfile name="requirements.txt" path="d:\graduate\zuohuiying-main\backend\requirements.txt"></mcfile>` |
| Passlib    | 1.7.4  | 密码哈希     | `<mcfile name="requirements.txt" path="d:\graduate\zuohuiying-main\backend\requirements.txt"></mcfile>` |

### 2.2 前端技术栈

| 技术/框架  | 版本 | 用途       | 来源                                                                                               |
| ---------- | ---- | ---------- | -------------------------------------------------------------------------------------------------- |
| Vue.js     | 3.x  | 前端框架   | `<mcfile name="package.json" path="d:\graduate\zuohuiying-main\frontend\package.json"></mcfile>` |
| Vue Router | -    | 路由管理   | `<mcfile name="package.json" path="d:\graduate\zuohuiying-main\frontend\package.json"></mcfile>` |
| Axios      | -    | HTTP客户端 | `<mcfile name="package.json" path="d:\graduate\zuohuiying-main\frontend\package.json"></mcfile>` |
| Vite       | -    | 构建工具   | `<mcfile name="package.json" path="d:\graduate\zuohuiying-main\frontend\package.json"></mcfile>` |

## 3. 系统架构

### 3.1 整体架构

系统采用前后端分离的架构设计：

- **前端**：Vue.js单页应用，负责用户界面渲染和交互
- **后端**：FastAPI RESTful API服务，负责业务逻辑处理和数据存储
- **数据库**：SQLite轻量级数据库，存储所有业务数据
- **数据库可视化工具**：基于Tkinter开发的桌面应用，用于直观管理和操作数据库内容

### 3.2 后端架构

后端采用模块化设计，主要包括以下模块：

- **API路由模块**：处理HTTP请求，包含认证、学生服务、教师服务和学校管理路由
- **数据模型模块**：定义数据库表结构和关系
- **认证模块**：处理用户注册、登录和令牌管理
- **异常处理**：全局异常捕获和处理
- **数据库可视化工具**：提供图形界面，用于直观管理和查看SQLite数据库内容

主要文件结构：

- `main.py`：应用入口，配置CORS、路由注册、异常处理等
- `db.py`：SQLite数据库可视化工具，提供图形界面用于管理和查看数据库内容
- `api/`：API路由模块目录
  - `auth.py`：认证相关API
  - `student.py`：学生服务API
  - `teacher.py`：教师服务API
  - `schools.py`：学校管理API
- `models/`：数据模型目录
  - `database.py`：数据库表定义

### 3.3 前端架构

前端采用Vue.js组件化开发，主要包括：

- **路由管理**：使用Vue Router实现页面导航
- **组件系统**：可复用UI组件
- **状态管理**：使用localStorage管理用户认证信息
- **视图页面**：首页、登录注册、学生中心、教师中心等

主要文件结构：

- `main.js`：应用入口
- `App.vue`：根组件
- `router/`：路由配置
- `views/`：页面视图组件
  - `student/`：学生相关页面
  - `teacher/`：教师相关页面

## 4. 后端API设计

### 4.1 认证API (`/auth`)

| 端点               | 方法 | 功能描述 | 请求体 (JSON)                                                                             | 成功响应 (200 OK)                                                                    |
| ------------------ | ---- | -------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `/auth/register` | POST | 用户注册 | `{"username": "...", "password": "...", "role": "student/teacher", "name": "...", ...}` | `{"user_id": "...", "username": "...", "role": "..."}`                             |
| `/auth/login`    | POST | 用户登录 | `{"username": "...", "password": "...", "role": "..."}`                                 | `{"access_token": "...", "refresh_token": "...", "user_id": "...", "role": "..."}` |
| `/auth/refresh`  | POST | 刷新令牌 | `{"refresh_token": "..."}`                                                              | `{"access_token": "..."}`                                                          |

### 4.2 学生服务API (`/student`)

| 端点                                    | 方法 | 功能描述         | 权限 | 成功响应         |
| --------------------------------------- | ---- | ---------------- | ---- | ---------------- |
| `/student/profile`                    | GET  | 获取学生资料     | 学生 | 学生资料对象     |
| `/student/profile`                    | PUT  | 更新学生资料     | 学生 | 更新后的学生资料 |
| `/student/recommend/schools`          | GET  | 获取学校推荐     | 学生 | 推荐学校列表     |
| `/student/schools`                    | GET  | 获取学校列表     | 学生 | 学校列表         |
| `/student/schools/search`             | GET  | 搜索学校         | 学生 | 搜索结果列表     |
| `/student/schools/{school_id}`        | GET  | 获取学校详情     | 学生 | 学校详情         |
| `/student/success-cases`              | GET  | 获取成功案例     | 学生 | 成功案例列表     |
| `/student/training/appointments`      | POST | 创建培训预约     | 学生 | 创建的预约信息   |
| `/student/training/appointments`      | GET  | 获取培训预约列表 | 学生 | 预约列表         |
| `/student/training/appointments/{id}` | GET  | 获取培训预约详情 | 学生 | 预约详情         |

### 4.3 教师服务API (`/teacher`)

| 端点                                    | 方法 | 功能描述         | 权限 | 成功响应         |
| --------------------------------------- | ---- | ---------------- | ---- | ---------------- |
| `/teacher/profile`                    | GET  | 获取教师资料     | 教师 | 教师资料对象     |
| `/teacher/profile`                    | PUT  | 更新教师资料     | 教师 | 更新后的教师资料 |
| `/teacher/statistics`                 | GET  | 获取学生统计数据 | 教师 | 统计数据         |
| `/teacher/students`                   | GET  | 获取学生列表     | 教师 | 学生列表         |
| `/teacher/prediction/success-rate`    | POST | 预测留学成功率   | 教师 | 预测结果         |
| `/teacher/training/appointments`      | GET  | 获取培训预约列表 | 教师 | 预约列表         |
| `/teacher/training/appointments/{id}` | PUT  | 更新培训预约状态 | 教师 | 更新后的预约信息 |

### 4.4 学校管理API (`/schools`)

| 端点              | 方法   | 功能描述     | 权限 | 成功响应         |
| ----------------- | ------ | ------------ | ---- | ---------------- |
| `/schools`      | GET    | 获取学校列表 | 公开 | 学校列表         |
| `/schools/{id}` | GET    | 获取学校详情 | 公开 | 学校详情         |
| `/schools`      | POST   | 创建学校     | 教师 | 创建的学校信息   |
| `/schools/{id}` | PUT    | 更新学校信息 | 教师 | 更新后的学校信息 |
| `/schools/{id}` | DELETE | 删除学校     | 教师 | 成功消息         |

## 5. 数据库设计

### 5.1 数据表结构

#### 5.1.1 users表

- **id**: 主键，用户ID
- **username**: 用户名（唯一）
- **password_hash**: 密码哈希
- **role**: 用户角色（student/teacher）
- **created_at**: 创建时间
- **updated_at**: 更新时间

#### 5.1.2 student_profiles表

- **user_id**: 外键，关联users表
- **name**: 学生姓名
- **age**: 年龄
- **gender**: 性别
- **current_education**: 当前教育程度
- **target_country**: 目标国家
- **gpa**: GPA成绩
- **english_score**: 英语成绩
- **major**: 专业
- **interests**: 兴趣爱好
- **updated_at**: 更新时间

#### 5.1.3 teacher_profiles表

- **user_id**: 外键，关联users表
- **name**: 教师姓名
- **specialization**: 专长领域
- **experience_years**: 工作经验
- **qualification**: 资质证书
- **bio**: 个人简介
- **contact_email**: 联系邮箱
- **updated_at**: 更新时间

#### 5.1.4 schools表

- **id**: 主键，学校ID
- **name**: 学校名称
- **country**: 所在国家
- **city**: 所在城市
- **ranking**: 排名
- **tuition_fee**: 学费
- **admission_rate**: 录取率
- **description**: 学校描述
- **created_at**: 创建时间
- **updated_at**: 更新时间

#### 5.1.5 school_majors表

- **id**: 主键
- **school_id**: 外键，关联schools表
- **major_name**: 专业名称
- **requirements**: 入学要求
- **course_description**: 课程描述

#### 5.1.6 training_reservations表

- **id**: 主键，预约ID
- **student_id**: 外键，关联users表
- **teacher_id**: 外键，关联users表
- **subject**: 培训科目
- **schedule_time**: 预约时间
- **duration**: 时长(小时)
- **status**: 状态（pending/completed/cancelled）
- **notes**: 备注
- **created_at**: 创建时间
- **updated_at**: 更新时间

#### 5.1.8 success_cases表

- **id**: 主键，案例ID
- **student_name**: 学生姓名
- **from_school**: 来自学校
- **admitted_school**: 录取学校
- **major**: 专业
- **gpa**: GPA
- **english_score**: 英语成绩
- **experience**: 经验分享
- **year**: 入学年份
- **created_at**: 创建时间

### 5.2 关系图

```
users 1:N student_profiles
users 1:N teacher_profiles
schools 1:N school_majors
users 1:N training_reservations (student)
users 1:N training_reservations (teacher)
users 1:N document_reservations (student)
users 1:N document_reservations (teacher)
```

## 6. 前端功能模块

### 6.1 认证模块

- 登录功能（支持学生/教师角色切换）
- 注册功能（支持学生/教师角色选择）
- JWT令牌管理与自动登录
- 角色权限验证

### 6.2 公共页面

- 首页：系统介绍、主要功能入口
- 学校库：公开的学校信息浏览
- 服务介绍：平台提供的服务详情
- 成功案例：成功留学案例展示
- 帮助中心：使用指南和常见问题

### 6.3 学生中心

- 个人资料管理：基本信息、教育背景、目标院校等
- 学校推荐：基于学生信息的智能推荐
- 学校搜索：按国家、专业、排名等条件筛选
- 语言培训预约：创建、查看培训预约

### 6.4 教师中心

- 个人资料管理：专业背景、联系方式等
- 学生统计：管理的学生数量、预约情况等
- 学生列表：查看和管理所有学生
- 留学预测：基于数据预测学生录取成功率
- 预约管理：处理语言培训和预约
- 学校管理：添加、编辑和删除学校信息

## 7. 权限与安全

### 7.1 用户角色

- **学生角色**：访问学生中心、预约服务、查看学校信息
- **教师角色**：访问教师中心、管理学生、处理预约、管理学校信息

### 7.2 安全机制

- JWT令牌认证
- 密码加密存储（bcrypt）
- 输入数据验证
- CORS配置
- 错误信息安全处理

## 8. 测试账号

### 8.1 学生账号

- **用户名**：testuser
- **密码**：testpass
- **角色**：student

### 8.2 教师账号

- **用户名**：teacheruser
- **密码**：teacherpass
- **角色**：teacher

## 9. 部署与运行

### 9.1 后端部署

#### 9.1.1 环境要求

- Python 3.7+
- pip包管理器
- SQLite数据库（Python标准库内置，无需单独安装）

#### 9.1.1.1 Python环境安装

如果未安装Python，可以通过以下方式安装：

**Windows系统：**

使用winget安装（推荐）：
```powershell
winget install Python.Python.3.11 --accept-source-agreements
```

或者从[Python官网](https://www.python.org/downloads/windows/)下载安装程序。

**注意：** 安装时请勾选"Add Python to PATH"选项，或安装后重启系统以确保Python命令在任何目录下都可用。

**验证安装：**
```powershell
python --version
pip --version
```

#### 9.1.2 安装与启动步骤

1. 进入后端目录：`cd backend`
2. 安装依赖：`pip install -r requirements.txt`
3. 配置环境变量（可选）：根据需要修改 `.env` 文件中的配置
4. 运行服务：`uvicorn main:app --reload`

**启动成功后：**
- API服务将在 http://127.0.0.1:8000 启动
- API文档可访问 http://127.0.0.1:8000/docs
- 自动重载模式已启用，代码修改后会自动重启服务

### 9.2 前端部署

#### 9.2.1 环境要求

- Node.js LTS版本（推荐16+）
- npm包管理器

> **说明：** 前端运行只需要Node.js环境，不需要Python环境。即使没有Python环境，也可以正常安装和启动前端开发服务器。但要使用完整功能，包括API调用，仍需启动后端服务，这就需要Python环境。

#### 9.2.2 安装与启动步骤

**前置条件**
确保已安装Node.js LTS版本。如果未安装，可以通过以下方式安装：

```bash
winget install OpenJS.NodeJS.LTS --accept-source-agreements
```

**安装依赖**

**重启系统后的简化方法（推荐）：**

如果系统已重启，直接在frontend目录下执行：

```powershell
cd d:\zuohuiying-main\frontend
npm install
```

**如果未重启系统，使用完整路径执行：**

```powershell
cd 'C:\Program Files\nodejs' ; .\node node_modules\npm\bin\npm-cli.js install --prefix 'd:\zuohuiying-main\frontend'
```

**注意：** 安装完Node.js后，重启系统可以解决路径问题，使node和npm命令在任何目录下直接可用。这是因为系统重启后，所有新的PowerShell会话都会加载更新后的环境变量。

**启动前端开发服务器**

**重启系统后的简化方法（推荐）：**

```powershell
cd d:\zuohuiying-main\frontend
npm run dev
```

**如果未重启系统，使用完整路径执行：**

```powershell
cd 'd:\zuohuiying-main\frontend' ; & 'C:\Program Files\nodejs\node' node_modules\vite\bin\vite.js
```

**启动成功后：**
- 前端开发服务将在 http://localhost:5173 启动
- 支持热重载，修改代码后自动更新
- 开发环境已配置跨域支持，可以直接调用后端API

**后端服务配置**

前端项目已配置API代理，将所有 `/api` 请求代理到 http://127.0.0.1:8000 后端服务。请确保后端服务已启动。

### 9.3 生产环境部署

#### 9.3.1 前端构建

```bash
cd frontend
npm run build
```

构建后的文件位于 `dist` 目录，可部署到静态文件服务器。

#### 9.3.2 后端部署

建议使用Gunicorn配合Nginx进行生产环境部署：

```bash
# 1. 安装Gunicorn
pip install gunicorn

# 2. 使用Gunicorn启动服务
cd backend
# 确保在backend目录下且虚拟环境已激活
uvicorn main:app --reload
```

**Nginx配置示例** (`/etc/nginx/sites-available/study-abroad`):

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端API代理
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**生产环境注意事项：**
1. 设置适当的环境变量（如数据库连接、密钥等）
2. 确保关闭调试模式
3. 配置HTTPS以提高安全性
4. 设置适当的日志记录
5. 考虑使用进程管理器（如systemd）管理服务





## 10. 数据库可视化工具

### 10.1 工具概述

`db.py`是一个基于Tkinter开发的SQLite数据库可视化管理工具，为项目提供了直观的数据库内容浏览和管理功能。该工具能够帮助开发人员和管理员在不编写SQL语句的情况下，方便地查看和操作数据库中的数据。

### 10.2 主要功能

- **数据库表浏览**：直观显示数据库中的所有表结构和记录
- **数据增删改查**：提供图形界面进行记录的添加、编辑和删除操作
- **数据搜索**：支持在当前表中搜索指定内容
- **SQL查询执行**：允许直接输入和执行SQL语句
- **数据库导出**：支持将数据导出为其他格式
- **多表切换**：便捷地在不同表之间切换查看

### 10.3 使用方法

1. 在backend目录下运行：`python db.py`
2. 程序会自动连接到默认的SQLite数据库
3. 在左侧面板选择要查看的数据库表
4. 使用工具栏按钮进行数据操作
5. 在搜索框中输入关键词进行数据搜索
6. 在SQL查询框中输入SQL语句并执行

### 10.4 工具优势

- **无需编写SQL**：通过图形界面即可完成常见的数据操作
- **实时数据更新**：操作后立即显示最新数据状态
- **便捷的数据浏览**：支持表格形式直观展示数据
- **搜索功能**：快速定位需要的数据记录
- **SQL查询支持**：同时保留高级查询功能

## 11. 总结

留学服务平台采用现代化的前后端分离架构，提供了完整的留学服务生态系统。后端使用FastAPI构建高性能RESTful API，前端采用Vue.js提供流畅的用户体验。系统支持学生和教师两种角色，实现了学校推荐、培训预约等核心功能，并通过JWT实现了安全的用户认证机制。

该系统具有良好的可扩展性，未来可以考虑添加更多功能，如留学申请进度跟踪、视频面试模拟、留学费用计算器等，进一步提升平台的服务质量和用户体验。同时，通过提供自动化安装脚本，大大简化了项目的部署和运行流程，便于快速启动和测试系统。