@echo off
chcp 65001 >nul
echo ========================================
echo 数据库迁移脚本：添加 room_id 字段
echo ========================================
echo.
echo 正在添加 room_id 字段到 alert_rules 表...
echo.

cd /d %~dp0\..\..
python migrations\add_room_id.py

if errorlevel 1 (
    echo.
    echo [错误] 迁移失败
    pause
    exit /b 1
)

echo.
echo [成功] 迁移完成
echo.
echo 提示：请手动更新320宿舍的room_id为5699（如果存在）
echo.
pause
