@echo off
chcp 65001 >nul
echo ========================================
echo 停止所有服务
echo ========================================
echo.

REM 设置端口
set BACKEND_PORT=8000
set FRONTEND_PORT=3000
set NONEBOT_PORT=8080

echo [1/4] 停止后端服务 (端口 %BACKEND_PORT%)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%BACKEND_PORT%" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
    echo [停止] 已停止进程 PID: %%a
)

echo.
echo [2/4] 停止前端服务 (端口 %FRONTEND_PORT%)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%FRONTEND_PORT%" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
    echo [停止] 已停止进程 PID: %%a
)

echo.
echo [3/4] 停止 NoneBot 服务 (端口 %NONEBOT_PORT%)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%NONEBOT_PORT%" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
    echo [停止] 已停止进程 PID: %%a
)

echo.
echo [4/4] 停止 NapCatQQ...
tasklist /FI "IMAGENAME eq NapCatQQ.exe" 2>NUL | find /I /N "NapCatQQ.exe">NUL
if "%ERRORLEVEL%"=="0" (
    taskkill /F /IM NapCatQQ.exe >nul 2>&1
    echo [停止] 已停止 NapCatQQ
) else (
    echo [提示] NapCatQQ 未运行
)

echo.
echo ========================================
echo 所有服务已停止
echo ========================================
echo.

timeout /t 2 /nobreak >nul
pause
