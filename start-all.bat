@echo off
chcp 65001 >nul
echo ========================================
echo 西华大学宿舍电费监控系统 - 一键启动
echo ========================================
echo.

REM 检查是否在项目根目录
if not exist "backend\run.py" (
    echo [错误] 请在项目根目录运行此脚本
    pause
    exit /b 1
)

echo [提示] 将启动两个窗口：
echo   1. 后端服务（端口 8000）
echo   2. 前端服务（端口 3000）
echo.
echo 按任意键继续...
pause >nul

REM 启动后端（新窗口）
start "后端服务 - 端口8000" cmd /k "cd /d %~dp0backend && scripts\start\start.bat"

REM 等待后端启动
timeout /t 3 /nobreak >nul

REM 启动前端（新窗口）
start "前端服务 - 端口3000" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ========================================
echo 启动完成！
echo ========================================
echo.
echo 后端服务: http://localhost:8000
echo 前端界面: http://localhost:3000
echo API文档:  http://localhost:8000/docs
echo.
echo 提示：两个服务窗口已打开，关闭窗口即可停止服务
echo.

pause
