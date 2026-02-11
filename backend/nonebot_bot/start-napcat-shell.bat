@echo off
chcp 65001 >nul
echo ========================================
echo NapCatQQ Shell 启动脚本
echo ========================================
echo.

REM 查找 NapCat Shell 安装目录
set "NAPCAT_DIR="
for /d %%d in ("C:\Users\71408\Desktop\NapCat.*Shell*") do (
    set "NAPCAT_DIR=%%d"
    goto :found
)

REM 如果没找到，尝试固定路径
if not defined NAPCAT_DIR (
    if exist "C:\Users\71408\Desktop\NapCat.44498.Shell" (
        set "NAPCAT_DIR=C:\Users\71408\Desktop\NapCat.44498.Shell"
        goto :found
    )
)

echo [错误] 未找到 NapCat Shell 安装目录
echo.
echo 请先运行安装程序：
echo 1. 进入：C:\Users\71408\Desktop\NapCat.Shell.Windows.OneKey
echo 2. 运行：NapCatInstaller.exe
echo 3. 等待安装完成
echo.
pause
exit /b 1

:found
echo [成功] 找到 NapCat 目录：%NAPCAT_DIR%
echo.

REM 检查 NoneBot 是否运行
echo [1/2] 检查 NoneBot 是否运行...
netstat -ano | findstr ":8080" >nul
if errorlevel 1 (
    echo [警告] NoneBot 可能未运行
    echo 请先启动 NoneBot：
    echo   cd C:\dorm-power-guard-lite\backend\nonebot_bot
    echo   python bot.py
    echo.
    echo 是否继续启动 NapCatQQ？（Y/N）
    set /p continue=
    if /i not "%continue%"=="Y" exit /b 1
)

REM 检查配置文件
set "CONFIG_FILE=%NAPCAT_DIR%\config\onebot11.json"
if not exist "%CONFIG_FILE%" (
    echo [提示] 配置文件不存在，首次运行后会自动生成
    echo 建议使用 WebUI 配置：http://localhost:6099/webui
    echo.
)

REM 复制配置文件模板（如果不存在）
if not exist "%NAPCAT_DIR%\config" (
    mkdir "%NAPCAT_DIR%\config"
)

set "TEMPLATE_FILE=%~dp0napcat-config.json"
if exist "%TEMPLATE_FILE%" (
    if not exist "%CONFIG_FILE%" (
        echo [提示] 复制配置文件模板...
        copy /Y "%TEMPLATE_FILE%" "%CONFIG_FILE%" >nul
        echo [成功] 配置文件已创建：%CONFIG_FILE%
        echo 请检查 WebSocket 地址：ws://localhost:8080/onebot/v11/ws
        echo.
    )
)

echo [2/2] 启动 NapCatQQ...
echo.
echo ========================================
echo NapCatQQ 启动中...
echo ========================================
echo.
echo 提示：
echo - 首次运行会显示二维码，用手机QQ扫描登录
echo - 登录成功后会自动连接到 NoneBot
echo - WebUI 配置地址：http://localhost:6099/webui
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

cd /d "%NAPCAT_DIR%"
call napcat.bat

pause
