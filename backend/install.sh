#!/bin/bash

echo "========================================"
echo "宿舍电费监控系统 - 依赖安装脚本"
echo "========================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到Python3，请先安装Python 3.8+"
    exit 1
fi

echo "[1/3] 检查Python版本..."
python3 --version

echo ""
echo "[2/3] 升级pip..."
python3 -m pip install --upgrade pip

echo ""
echo "[3/3] 安装项目依赖..."
python3 -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "[错误] 依赖安装失败，请检查网络连接或pip配置"
    exit 1
fi

echo ""
echo "========================================"
echo "依赖安装完成！"
echo "========================================"
echo ""
echo "下一步："
echo "1. 复制 .env.example 为 .env 并配置"
echo "2. 创建MySQL数据库"
echo "3. 运行 python3 run.py 启动服务"
echo ""
