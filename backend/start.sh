#!/bin/bash

echo "========================================"
echo "宿舍电费监控系统 - 启动脚本"
echo "========================================"
echo ""

# 检查.env文件
if [ ! -f .env ]; then
    echo "[警告] 未找到 .env 文件"
    echo "正在从 .env.example 创建..."
    cp .env.example .env
    echo "请编辑 .env 文件配置数据库等信息"
    echo ""
    exit 1
fi

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到Python3"
    exit 1
fi

echo "[1/2] 检查依赖..."
python3 -c "import fastapi" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[警告] 依赖未安装，正在安装..."
    python3 -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[错误] 依赖安装失败"
        exit 1
    fi
fi

echo "[2/2] 启动服务..."
echo ""
echo "服务将在 http://localhost:8000 启动"
echo "API文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

python3 run.py
