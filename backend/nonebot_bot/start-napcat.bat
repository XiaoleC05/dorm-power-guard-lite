@echo off
chcp 65001 >nul
echo ========================================
echo NapCatQQ 启动脚本
echo ========================================
echo.

REM 检查 NapCatQQ 是否存在
if not exist "C:\Users\71408\Desktop\NapCatQQ.exe" (
    echo [错误] 未找到 NapCatQQ.exe
    echo.
    echo 请先下载 NapCatQQ：
    echo 1. 访问：https://github.com/NapNeko/NapCatQQ/releases
    echo 2. 下载 NapCatQQ-windows-amd64.exe
    echo 3. 重命名为 NapCatQQ.exe 并放到桌面
    echo.
    pause
    exit /b 1
)

REM 检查配置文件目录是否存在
if not exist "C:\Users\71408\Desktop\config" (
    echo [提示] 创建 config 目录...
    mkdir "C:\Users\71408\Desktop\config"
)

REM 检查配置文件是否存在
if not exist "C:\Users\71408\Desktop\config\onebot11.json" (
    echo [提示] 未找到 onebot11.json，正在复制配置文件...
    copy /Y "%~dp0napcat-config.json" "C:\Users\71408\Desktop\config\onebot11.json" >nul
    if errorlevel 1 (
        echo [错误] 配置文件复制失败
        pause
        exit /b 1
    )
    echo [成功] 配置文件已复制到：C:\Users\71408\Desktop\config\onebot11.json
    echo.
)

echo [1/2] 检查 NoneBot 是否运行...
netstat -ano | findstr ":8080" >nul
if errorlevel 1 (
    echo [警告] NoneBot 可能未运行
    echo 请先启动 NoneBot：
    echo   cd C:\dorm-power-guard-lite\backend\nonebot_bot
    echo   python bot.py
    echo.
    pause
)

echo [2/2] 启动 NapCatQQ...
echo.
echo ========================================
echo NapCatQQ 启动中...
echo ========================================
echo.
echo 提示：
echo - 如果使用扫码登录，会显示二维码
echo - 登录成功后会自动连接到 NoneBot
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

cd /d C:\Users\71408\Desktop
NapCatQQ.exe

pause
