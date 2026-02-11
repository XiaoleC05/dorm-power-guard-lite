@echo off
REM 安全删除数据库中多余表的批处理脚本（使用Python脚本）
REM 
REM 此脚本会自动检测并删除不在代码中定义的表
REM 当前代码中定义的表：
REM   1. power_records - 电费记录表
REM   2. alert_rules - 告警规则表
REM   3. alert_logs - 告警日志表
REM
REM 使用方法：双击运行

echo ========================================
echo 删除数据库中多余的表（Python版本）
echo ========================================
echo.

cd /d "%~dp0\..\..\.."

REM 执行Python脚本
python backend\scripts\db\drop_unused_tables.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo 操作完成！
    echo ========================================
) else (
    echo.
    echo ========================================
    echo 操作失败，请检查错误信息
    echo ========================================
)

pause
