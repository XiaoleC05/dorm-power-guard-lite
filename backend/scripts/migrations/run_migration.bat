@echo off
chcp 65001 >nul
echo ========================================
echo 数据库迁移脚本
echo ========================================
echo.
echo 正在添加 qq_receiver_id 字段到 alert_rules 表...
echo.

cd /d %~dp0\..\..
python migrations\add_qq_receiver_id.py

if errorlevel 1 (
    echo.
    echo [错误] 迁移失败
    pause
    exit /b 1
)

echo.
echo [成功] 迁移完成
echo.
pause
