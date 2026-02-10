#!/bin/bash
# 代码更新脚本 - 自动拉取最新代码并重启服务

set -e

echo "=========================================="
echo "开始更新代码..."
echo "=========================================="

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# 备份当前代码
echo ""
echo "1. 备份当前代码..."
BACKUP_DIR="/opt/backups/code"
mkdir -p "$BACKUP_DIR"
BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).tar.gz"
tar -czf "$BACKUP_FILE" . --exclude='.git' --exclude='node_modules' --exclude='__pycache__' 2>/dev/null || true
echo "   备份已保存到: $BACKUP_FILE"

# 检查是否有未提交的更改
if [ -n "$(git status -s)" ]; then
    echo ""
    echo "[警告] 检测到未提交的更改："
    git status -s
    read -p "是否继续更新？未提交的更改可能会丢失 (y/N): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        echo "更新已取消"
        exit 1
    fi
fi

# 拉取最新代码
echo ""
echo "2. 拉取最新代码..."
git fetch origin
CURRENT_BRANCH=$(git branch --show-current)
git pull origin "$CURRENT_BRANCH"

# 显示更新内容
echo ""
echo "3. 更新内容："
git log HEAD~1..HEAD --oneline

# 更新Python依赖
echo ""
echo "4. 更新Python依赖..."
cd backend
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt --quiet
    echo "   Python依赖已更新"
fi

# 运行数据库迁移（如果有）
if [ -f "apply_migration.py" ]; then
    echo ""
    echo "5. 检查数据库迁移..."
    python3 apply_migration.py
fi

# 重启服务
echo ""
echo "6. 重启服务..."
if systemctl is-active --quiet dorm-power-guard 2>/dev/null; then
    sudo systemctl restart dorm-power-guard
    echo "   服务已重启"
else
    echo "   [提示] 服务未运行，跳过重启"
fi

# 等待服务启动
sleep 3

# 检查服务状态
echo ""
echo "7. 检查服务状态..."
if systemctl is-active --quiet dorm-power-guard 2>/dev/null; then
    echo "=========================================="
    echo "✅ 更新成功！服务运行正常"
    echo "=========================================="
    echo ""
    echo "查看服务状态: sudo systemctl status dorm-power-guard"
    echo "查看服务日志: sudo journalctl -u dorm-power-guard -f"
else
    echo "=========================================="
    echo "⚠️  警告：服务可能未正常启动"
    echo "=========================================="
    echo ""
    echo "请检查日志: sudo journalctl -u dorm-power-guard -n 50"
    echo "如需回滚: cd $PROJECT_DIR && git reset --hard HEAD~1"
fi
