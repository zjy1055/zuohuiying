@echo off
cls
echo 开始自动配置留学服务平台环境...
echo ====================================

REM 检查Python是否已安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 未检测到Python，开始下载安装...
    REM 下载Python安装包
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.4/python-3.11.4-amd64.exe' -OutFile 'python-installer.exe'"
    
    REM 静默安装Python并添加到PATH
    echo 正在安装Python，请稍候...
    python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    
    REM 删除安装包
    del python-installer.exe
    
    REM 刷新环境变量
    set PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%LOCALAPPDATA%\Programs\Python\Python311
    
    echo Python安装完成！
) else (
    echo Python已安装，版本：
    python --version
)

REM 检查Node.js是否已安装
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 未检测到Node.js，开始下载安装...
    REM 下载Node.js安装包
    powershell -Command "Invoke-WebRequest -Uri 'https://nodejs.org/dist/v18.16.0/node-v18.16.0-x64.msi' -OutFile 'node-installer.msi'"
    
    REM 静默安装Node.js
    echo 正在安装Node.js，请稍候...
    msiexec /i node-installer.msi /qn
    
    REM 删除安装包
    del node-installer.msi
    
    REM 刷新环境变量
    set PATH=%PATH%;%PROGRAMFILES%\nodejs;%APPDATA%\npm
    
    echo Node.js安装完成！
) else (
    echo Node.js已安装，版本：
    node --version
)

REM 安装pip包管理工具（如果需要）
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装pip...
    powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'get-pip.py'; python get-pip.py; del get-pip.py"
)

echo ====================================
echo 环境配置完成，开始安装项目依赖...

REM 创建后端依赖安装和启动脚本
(echo @echo off
echo cd backend
echo echo 正在安装Python依赖...
echo pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
echo echo 正在初始化数据库...
echo python add_test_data_complete.py
echo echo 启动后端服务...
echo uvicorn main:app --reload) > start_backend.bat

REM 创建前端依赖安装和启动脚本
(echo @echo off
echo cd frontend
echo echo 正在安装npm依赖...
echo npm install --registry=https://registry.npmmirror.com
echo echo 启动前端服务...
echo npm run dev) > start_frontend.bat

echo ====================================
echo 项目启动准备就绪！
echo 即将启动后端服务...

REM 启动后端服务
start "后端服务" cmd /k call start_backend.bat

REM 等待后端服务初始化
ping 127.0.0.1 -n 5 > nul

echo 即将启动前端服务...
echo ====================================
echo 项目启动说明：
echo 1. 后端服务将在 http://127.0.0.1:8000 启动
echo 2. 前端服务将在 http://localhost:5173 启动
echo 3. 请在浏览器中访问 http://localhost:5173 使用系统
echo 4. 测试账号：
echo    - 学生：用户名testuser，密码testpass
echo    - 教师：用户名teacheruser，密码teacherpass
echo ====================================

REM 启动前端服务
start "前端服务" cmd /k call start_frontend.bat

REM 打开浏览器访问系统
ping 127.0.0.1 -n 10 > nul
start http://localhost:5173

echo 安装和启动脚本已创建：
echo - start_backend.bat：单独启动后端服务
echo - start_frontend.bat：单独启动前端服务
echo - setup_and_run.bat：完整安装和启动流程
echo 
echo 如果需要手动启动服务，请分别运行 start_backend.bat 和 start_frontend.bat
echo 按任意键退出...
pause >nul