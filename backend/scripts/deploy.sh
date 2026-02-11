#!/bin/bash
# 快速部署脚本（适用于Ubuntu/Debian系统）

set -e

echo "=========================================="
echo "宿舍电费监控系统 - 快速部署脚本"
echo "=========================================="
echo ""

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then 
    echo "请使用root用户运行此脚本"
    exit 1
fi

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
cd "$BACKEND_DIR"

# 安装依赖
echo "1. 安装系统依赖..."
apt update
apt install -y python3 python3-pip git mysql-server nginx

# 安装Python依赖
echo "2. 安装Python依赖..."
pip3 install -r requirements.txt

# 配置MySQL
echo "3. 配置MySQL..."
read -p "请输入MySQL root密码: " MYSQL_ROOT_PASSWORD
read -p "请输入数据库用户名: " DB_USER
read -p "请输入数据库密码: " DB_PASSWORD

mysql -u root -p$MYSQL_ROOT_PASSWORD <<EOF
CREATE DATABASE IF NOT EXISTS dorm_power_guard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON dorm_power_guard.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
EOF

# 配置环境变量
echo "4. 配置环境变量..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "请编辑 backend/.env 文件，配置数据库和其他参数"
    read -p "按Enter继续..."
fi

# 创建systemd服务
echo "5. 创建systemd服务..."
cat > /etc/systemd/system/dorm-power-guard.service <<EOF
[Unit]
Description=Dorm Power Guard Backend Service
After=network.target mysql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=$BACKEND_DIR
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 $BACKEND_DIR/run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable dorm-power-guard
systemctl start dorm-power-guard

echo ""
echo "=========================================="
echo "部署完成！"
echo "=========================================="
echo ""
echo "服务状态:"
systemctl status dorm-power-guard --no-pager
echo ""
echo "查看日志: sudo journalctl -u dorm-power-guard -f"
echo "重启服务: sudo systemctl restart dorm-power-guard"
echo ""
