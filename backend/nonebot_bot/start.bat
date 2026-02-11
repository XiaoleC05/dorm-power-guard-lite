@echo off
chcp 65001 >nul
echo ========================================
echo NoneBot QQ机器人启动脚本
echo ========================================
echo.

cd /d %~dp0

echo [1/2] 检查依赖...
python -c "import nonebot" >nul 2>&1
if errorlevel 1 (
    echo [错误] NoneBot 未安装
    echo 正在安装依赖...
    pip install nonebot2 nonebot-adapter-onebot
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
)

echo [2/2] 启动 NoneBot...
echo.
echo ========================================
echo NoneBot 服务启动中...
echo ========================================
echo.
echo HTTP API 地址: http://localhost:8080
echo API 文档: http://localhost:8080/docs
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

python bot.py

pause
