@echo off
REM 启用错误处理：遇到错误时继续执行但显示错误
setlocal enabledelayedexpansion
set "ERROR_OCCURRED=0"

REM 设置代码页为UTF-8
chcp 65001 >nul 2>&1

REM ========================================
REM 西华大学宿舍电费监控系统 - 完整启动脚本
REM ========================================

title 宿舍电费监控系统 - 完整启动

echo ========================================
echo 西华大学宿舍电费监控系统 - 完整启动
echo ========================================
echo.
echo [提示] 当前目录: %CD%
echo [提示] 脚本路径: %~dp0
echo.

REM 检查是否在项目根目录
cd /d %~dp0
if not exist "backend\run.py" (
    echo [错误] 请在项目根目录运行此脚本
    echo 当前目录: %CD%
    echo 请确保脚本在项目根目录，且存在 backend\run.py 文件
    echo.
    pause
    exit /b 1
)

REM 设置变量
set BACKEND_PORT=8000
set FRONTEND_PORT=3000
set NONEBOT_PORT=8080
set NAPCAT_PATH=C:\Users\71408\Desktop\NapCatQQ.exe

echo [步骤 1/6] 检查环境...
echo.

REM 检查Python
echo [检查] 正在检查Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python
    echo 请确保Python已安装并添加到PATH环境变量
    echo.
    pause
    exit /b 1
) else (
    REM 使用临时文件避免PATH中的特殊字符问题
    python --version >"%TEMP%\python_version.txt" 2>&1
    if exist "%TEMP%\python_version.txt" (
        for /f "usebackq delims=" %%i in ("%TEMP%\python_version.txt") do echo [检查] %%i
        del "%TEMP%\python_version.txt" >nul 2>&1
    )
)

REM 检查Node.js
echo [检查] 正在检查Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [警告] 未检测到Node.js，前端服务将无法启动
    echo 请安装Node.js: https://nodejs.org/
    echo.
) else (
    REM 使用临时文件避免PATH中的特殊字符问题
    node --version >"%TEMP%\node_version.txt" 2>&1
    if exist "%TEMP%\node_version.txt" (
        for /f "usebackq delims=" %%i in ("%TEMP%\node_version.txt") do echo [检查] Node.js: %%i
        del "%TEMP%\node_version.txt" >nul 2>&1
    )
)

REM 检查.env文件
if not exist "backend\.env" (
    echo [警告] 未找到 backend\.env 文件
    if exist "backend\.env.example" (
        echo 正在从 .env.example 创建...
        copy "backend\.env.example" "backend\.env" >nul
        echo [提示] 请编辑 backend\.env 文件配置数据库等信息
        echo.
    ) else (
        echo [错误] 未找到 .env.example 文件
        pause
        exit /b 1
    )
)

echo [Step 2/6] Checking and stopping running services...
echo.

REM 停止占用端口的进程（使用临时文件避免编码问题）
REM 停止后端服务
netstat -ano | findstr ":%BACKEND_PORT%" >nul
if not errorlevel 1 (
    echo [Stop] Stopping backend service on port %BACKEND_PORT%...
    netstat -ano | findstr ":%BACKEND_PORT%" | findstr "LISTENING" >"%TEMP%\backend_pids.txt" 2>nul
    if exist "%TEMP%\backend_pids.txt" (
        for /f "tokens=5" %%a in ("%TEMP%\backend_pids.txt") do (
            taskkill /F /PID %%a >nul 2>&1
        )
        del "%TEMP%\backend_pids.txt" >nul 2>&1
    )
    timeout /t 2 /nobreak >nul
)

REM 停止前端服务
netstat -ano | findstr ":%FRONTEND_PORT%" >nul
if not errorlevel 1 (
    echo [Stop] Stopping frontend service on port %FRONTEND_PORT%...
    netstat -ano | findstr ":%FRONTEND_PORT%" | findstr "LISTENING" >"%TEMP%\frontend_pids.txt" 2>nul
    if exist "%TEMP%\frontend_pids.txt" (
        for /f "tokens=5" %%a in ("%TEMP%\frontend_pids.txt") do (
            taskkill /F /PID %%a >nul 2>&1
        )
        del "%TEMP%\frontend_pids.txt" >nul 2>&1
    )
    timeout /t 2 /nobreak >nul
)

REM 停止NoneBot服务
netstat -ano | findstr ":%NONEBOT_PORT%" >nul
if not errorlevel 1 (
    echo [Stop] Stopping NoneBot service on port %NONEBOT_PORT%...
    netstat -ano | findstr ":%NONEBOT_PORT%" | findstr "LISTENING" >"%TEMP%\nonebot_pids.txt" 2>nul
    if exist "%TEMP%\nonebot_pids.txt" (
        for /f "tokens=5" %%a in ("%TEMP%\nonebot_pids.txt") do (
            taskkill /F /PID %%a >nul 2>&1
        )
        del "%TEMP%\nonebot_pids.txt" >nul 2>&1
    )
    timeout /t 2 /nobreak >nul
)

REM 停止NapCatQQ进程
tasklist /FI "IMAGENAME eq NapCatQQ.exe" 2>NUL | find /I /N "NapCatQQ.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [Stop] Stopping NapCatQQ...
    taskkill /F /IM NapCatQQ.exe >nul 2>&1
    timeout /t 2 /nobreak >nul
)

echo.
echo [Step 3/6] Checking dependencies...
echo.

REM 检查后端依赖
echo [Check] Checking backend dependencies...
cd /d "%~dp0backend"
if errorlevel 1 (
    echo [错误] 无法切换到backend目录
    echo 当前目录: %CD%
    echo 脚本路径: %~dp0
    echo.
    pause
    exit /b 1
)

python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo [安装] 正在安装后端依赖...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 后端依赖安装失败
        echo 请检查网络连接或手动运行: pip install -r requirements.txt
        pause
        exit /b 1
    )
) else (
    echo [检查] 后端依赖已安装
)

REM 检查NoneBot依赖
echo [检查] 正在检查 NoneBot 依赖...
cd /d "%~dp0backend\nonebot_bot"
if errorlevel 1 (
    echo [警告] 无法切换到nonebot_bot目录，跳过NoneBot检查
    echo 当前目录: %CD%
    cd /d "%~dp0"
) else (
    python -c "import nonebot" >nul 2>&1
    if errorlevel 1 (
        echo [安装] 正在安装 NoneBot 依赖...
        pip install nonebot2 nonebot-adapter-onebot httpx
        if errorlevel 1 (
            echo [警告] NoneBot 依赖安装失败，QQ机器人功能可能无法使用
        )
    ) else (
        echo [检查] NoneBot 依赖已安装
    )
    cd /d "%~dp0"
)

REM 检查前端依赖
echo [检查] 正在检查前端依赖...
cd /d "%~dp0"
if exist "frontend\node_modules" (
    echo [检查] 前端依赖已安装
) else (
    echo [安装] 正在安装前端依赖...
    cd /d "%~dp0frontend"
    if errorlevel 1 (
        echo [警告] 无法切换到frontend目录，跳过前端依赖安装
        echo 当前目录: %CD%
        cd /d "%~dp0"
    ) else (
        call npm install
        if errorlevel 1 (
            echo [警告] 前端依赖安装失败
            echo 请检查网络连接或手动运行: npm install
        )
        cd /d "%~dp0"
    )
)

echo.
echo [Step 4/6] Starting backend service...
echo.

REM 启动后端（新窗口）
echo [Start] Starting backend service...
set "BACKEND_DIR=%~dp0backend"

REM 检查目录是否存在
if not exist "%BACKEND_DIR%\run.py" (
    echo [Error] Backend directory or run.py not found!
    echo Expected: %BACKEND_DIR%\run.py
    pause
    exit /b 1
)

echo [Info] Backend directory: %BACKEND_DIR%
start "Backend Service - Port %BACKEND_PORT%" cmd /k "title Backend Service - Port %BACKEND_PORT% && cd /d %BACKEND_DIR% && python run.py"
if errorlevel 1 (
    echo [Error] Failed to start backend service window
    echo Please check if Python is installed correctly
    echo Directory: %BACKEND_DIR%
    echo.
    pause
    exit /b 1
) else (
    echo [Success] Backend service window opened
)
timeout /t 5 /nobreak >nul

REM 检查后端是否启动成功
echo [Check] Checking backend service status...
timeout /t 3 /nobreak >nul

REM 尝试使用curl检查（如果可用）
where curl >nul 2>&1
if errorlevel 1 (
    echo [Info] curl not installed, skipping health check
    echo [Info] Please check backend window manually to confirm service is running
) else (
    curl -s http://localhost:%BACKEND_PORT%/health >nul 2>&1
    if errorlevel 1 (
        echo [Warning] Backend service may not have started properly, check backend window for errors
    ) else (
        echo [Success] Backend service started: http://localhost:%BACKEND_PORT%
    )
)

echo.
echo [Step 5/6] Starting NoneBot QQ bot...
echo.

REM 检查NapCat配置文件
if not exist "%USERPROFILE%\Desktop\config" (
    mkdir "%USERPROFILE%\Desktop\config"
)

if not exist "%USERPROFILE%\Desktop\config\onebot11.json" (
    echo [Config] Copying NapCat config file...
    copy /Y "%~dp0backend\nonebot_bot\napcat-config.json" "%USERPROFILE%\Desktop\config\onebot11.json" >nul
    if errorlevel 1 (
        echo [Warning] Failed to copy config file, please configure manually
    )
)

REM 启动NoneBot（新窗口）
echo [Start] Starting NoneBot service...
set "NONEBOT_DIR=%~dp0backend\nonebot_bot"

REM 检查目录是否存在
if not exist "%NONEBOT_DIR%\bot.py" (
    echo [Warning] NoneBot directory or bot.py not found, skipping...
    echo Expected: %NONEBOT_DIR%\bot.py
) else (
    echo [Info] NoneBot directory: %NONEBOT_DIR%
    start "NoneBot QQ Bot - Port %NONEBOT_PORT%" cmd /k "title NoneBot QQ Bot - Port %NONEBOT_PORT% && cd /d %NONEBOT_DIR% && python bot.py"
    if errorlevel 1 (
        echo [Warning] Failed to start NoneBot service window
        echo NoneBot may not be installed, QQ bot feature will be unavailable
        echo Directory: %NONEBOT_DIR%
    ) else (
        echo [Success] NoneBot service window opened
        timeout /t 5 /nobreak >nul
    )
)

REM 检查NoneBot是否启动成功
echo [Check] Checking NoneBot service status...
timeout /t 3 /nobreak >nul

REM 尝试使用curl检查（如果可用）
where curl >nul 2>&1
if errorlevel 1 (
    echo [Info] curl not installed, skipping health check
    echo [Info] Please check NoneBot window manually to confirm service is running
) else (
    curl -s http://localhost:%NONEBOT_PORT%/docs >nul 2>&1
    if errorlevel 1 (
        echo [Warning] NoneBot service may not have started properly, check NoneBot window for errors
    ) else (
        echo [Success] NoneBot service started: http://localhost:%NONEBOT_PORT%
    )
)

echo.
echo [Step 6/6] Starting NapCatQQ and frontend service...
echo.

REM 检查NapCatQQ是否存在（支持多个可能路径）
set NAPCAT_FOUND=0
if exist "%NAPCAT_PATH%" (
    set NAPCAT_FOUND=1
) else if exist "%USERPROFILE%\Desktop\NapCatQQ\NapCatQQ.exe" (
    set NAPCAT_PATH=%USERPROFILE%\Desktop\NapCatQQ\NapCatQQ.exe
    set NAPCAT_FOUND=1
) else if exist "%CD%\NapCatQQ.exe" (
    set NAPCAT_PATH=%CD%\NapCatQQ.exe
    set NAPCAT_FOUND=1
)

if !NAPCAT_FOUND!==1 (
    echo [Start] Starting NapCatQQ...
    start "NapCatQQ" "%NAPCAT_PATH%"
    timeout /t 3 /nobreak >nul
    echo [Info] NapCatQQ window opened
    echo.
    echo ========================================
    echo [重要] NapCatQQ 登录提示
    echo ========================================
    echo.
    echo 1. 如果使用扫码登录：
    echo    - NapCatQQ 窗口会显示二维码
    echo    - 使用手机QQ扫描二维码登录
    echo    - 登录成功后会自动连接到 NoneBot
    echo.
    echo 2. 如果使用账号密码登录：
    echo    - 在 NapCatQQ 窗口中输入QQ号和密码
    echo    - 登录成功后会自动连接到 NoneBot
    echo.
    echo 3. 连接成功后，NoneBot 窗口会显示连接信息
    echo.
    echo ========================================
    echo.
) else (
    echo [警告] 未找到 NapCatQQ.exe
    echo.
    echo 已检查的路径：
    echo   - %USERPROFILE%\Desktop\NapCatQQ.exe
    echo   - %USERPROFILE%\Desktop\NapCatQQ\NapCatQQ.exe
    echo   - %CD%\NapCatQQ.exe
    echo.
    echo 请手动启动 NapCatQQ：
    echo 1. 下载 NapCatQQ: https://github.com/NapNeko/NapCatQQ/releases
    echo 2. 将 NapCatQQ.exe 放到桌面或项目根目录
    echo 3. 或修改脚本中的 NAPCAT_PATH 变量指向实际路径
    echo.
)

REM 启动前端（新窗口）
cd /d "%~dp0"
if exist "frontend\node_modules" (
    echo [Start] Starting frontend service...
    set "FRONTEND_DIR=%~dp0frontend"
    
    REM 检查目录是否存在
    if not exist "%FRONTEND_DIR%\package.json" (
        echo [Warning] Frontend directory or package.json not found, skipping...
        echo Expected: %FRONTEND_DIR%\package.json
    ) else (
        echo [Info] Frontend directory: %FRONTEND_DIR%
        start "Frontend Service - Port %FRONTEND_PORT%" cmd /k "title Frontend Service - Port %FRONTEND_PORT% && cd /d %FRONTEND_DIR% && npm run dev"
        if errorlevel 1 (
            echo [Warning] Failed to start frontend service window
            echo Please check if Node.js is installed correctly
            echo Directory: %FRONTEND_DIR%
        ) else (
            echo [Success] Frontend service window opened
            timeout /t 3 /nobreak >nul
            echo [Success] Frontend service started: http://localhost:%FRONTEND_PORT%
        )
    )
) else (
    echo [Skip] Frontend dependencies not installed, skipping frontend startup
    echo [Tip] To start frontend, run: cd frontend && npm install
)

echo.
echo ========================================
echo 启动完成！
echo ========================================
echo.
echo 服务地址：
echo   - 后端服务:  http://localhost:%BACKEND_PORT%
echo   - API文档:   http://localhost:%BACKEND_PORT%/docs
echo   - 前端界面:  http://localhost:%FRONTEND_PORT%
echo   - NoneBot:   http://localhost:%NONEBOT_PORT%
echo.
echo 服务窗口：
echo   - 后端服务窗口：显示后端日志（标题：Backend Service - Port %BACKEND_PORT%）
echo   - NoneBot窗口：显示QQ机器人日志（标题：NoneBot QQ Bot - Port %NONEBOT_PORT%）
echo   - NapCatQQ窗口：显示登录二维码（如需要）
echo   - 前端服务窗口：显示前端构建日志（标题：Frontend Service - Port %FRONTEND_PORT%）
echo.
echo [提示] 如果看不到服务窗口：
echo   - 检查任务栏是否有最小化的窗口
echo   - 查看任务管理器中的进程（python.exe, node.exe）
echo.
echo ========================================
echo [重要提示]
echo ========================================
echo.
echo 1. NapCatQQ 登录：
echo    - 查看 NapCatQQ 窗口，按提示扫码或输入账号密码
echo    - 登录成功后会自动连接到 NoneBot
echo.
echo 2. 检查连接状态：
echo    - 查看 NoneBot 窗口，应该显示 "连接成功" 或类似信息
echo    - 如果连接失败，检查配置文件路径和端口设置
echo.
echo 3. 停止服务：
echo    - 关闭各个服务窗口即可停止服务
echo    - 或运行 stop-all.bat 脚本停止所有服务
echo.
echo ========================================
echo.
echo [完成] 脚本执行完成
echo.
echo [提示] 如果遇到问题：
echo   1. 查看上面的错误信息
echo   2. 检查各个服务窗口的错误日志（可能在任务栏）
echo   3. 运行 start-all-complete-debug.bat 获取详细调试信息
echo.

REM 简单检查服务状态
echo [提示] 正在检查服务状态...
timeout /t 2 /nobreak >nul

netstat -ano | findstr ":%BACKEND_PORT%" >nul
if errorlevel 1 (
    echo [后端] 端口 %BACKEND_PORT% 未被占用
) else (
    echo [后端] 端口 %BACKEND_PORT% 已被占用 - 后端服务正在运行
)

netstat -ano | findstr ":%FRONTEND_PORT%" >nul
if errorlevel 1 (
    echo [前端] 端口 %FRONTEND_PORT% 未被占用
) else (
    echo [前端] 端口 %FRONTEND_PORT% 已被占用 - 前端服务正在运行
)

netstat -ano | findstr ":%NONEBOT_PORT%" >nul
if errorlevel 1 (
    echo [NoneBot] 端口 %NONEBOT_PORT% 未被占用
) else (
    echo [NoneBot] 端口 %NONEBOT_PORT% 已被占用 - NoneBot服务正在运行
)

echo.
echo [提示] 服务窗口标题：
echo   - Backend Service - Port %BACKEND_PORT%
echo   - NoneBot QQ Bot - Port %NONEBOT_PORT%
echo   - Frontend Service - Port %FRONTEND_PORT%
echo.
echo [提示] 如果看不到窗口，请检查任务栏
echo [提示] 按任意键关闭此窗口（服务将继续运行）...
pause >nul
exit /b 0

REM ========================================
REM 脚本结束
REM ========================================
