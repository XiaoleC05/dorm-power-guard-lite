#!/usr/bin/env bash
# 一次性：从旧路径/服务名迁移到 DormGuard
set -euo pipefail

OLD_DIR="/opt/DormGuard"
NEW_DIR="/opt/DormGuard"

echo "[1] 停止旧 systemd 服务..."
systemctl stop dorm-backend dorm-nonebot dorm-healthcheck.timer 2>/dev/null || true
systemctl disable dorm-backend dorm-nonebot dorm-healthcheck.timer 2>/dev/null || true
systemctl stop dormguard-backend dormguard-nonebot dormguard-healthcheck.timer 2>/dev/null || true

echo "[2] 迁移应用目录 ${OLD_DIR} -> ${NEW_DIR}..."
if [ -d "$OLD_DIR" ]; then
  if [ -d "$NEW_DIR" ]; then
    rsync -a "$OLD_DIR/" "$NEW_DIR/"
    mv "${OLD_DIR}" "${OLD_DIR}.bak.$(date +%Y%m%d%H%M)" 2>/dev/null || true
  else
    mv "$OLD_DIR" "$NEW_DIR"
  fi
elif [ ! -d "$NEW_DIR" ]; then
  echo "错误：未找到 $OLD_DIR 或 $NEW_DIR"
  exit 1
fi

echo "[3] 清理旧 unit 文件..."
rm -f /etc/systemd/system/dorm-backend.service
rm -f /etc/systemd/system/dorm-nonebot.service
rm -f /etc/systemd/system/dorm-healthcheck.service
rm -f /etc/systemd/system/dorm-healthcheck.timer

echo "[4] 更新 Runner sudoers（若存在）..."
SUDOERS="/etc/sudoers.d/github-runner"
if [ -f "$SUDOERS" ]; then
  sed -i "s|/opt/DormGuard|/opt/DormGuard|g" "$SUDOERS"
  sed -i "s|/tmp/dormguard-release|/tmp/dormguard-release|g" "$SUDOERS"
  visudo -cf "$SUDOERS"
fi

echo "[5] 应用最新部署包中的 systemd/nginx（若已解压 release）..."
if [ -f "$NEW_DIR/deploy/apply-release.sh" ]; then
  bash "$NEW_DIR/deploy/apply-release.sh" "$NEW_DIR" 2>/dev/null || {
    cp "$NEW_DIR/deploy/systemd/"*.service /etc/systemd/system/ 2>/dev/null || true
    cp "$NEW_DIR/deploy/systemd/"*.timer /etc/systemd/system/ 2>/dev/null || true
    cp "$NEW_DIR/deploy/nginx/oxelia51.com.conf" /etc/nginx/sites-available/oxelia51.com
    ln -sf /etc/nginx/sites-available/oxelia51.com /etc/nginx/sites-enabled/oxelia51.com
    systemctl daemon-reload
    systemctl enable --now dormguard-healthcheck.timer
    systemctl restart dormguard-backend dormguard-nonebot
    nginx -t && systemctl reload nginx
  }
else
  systemctl daemon-reload
  systemctl enable --now dormguard-healthcheck.timer
  systemctl restart dormguard-backend dormguard-nonebot 2>/dev/null || true
fi

echo "[6] 状态"
systemctl is-active dormguard-backend dormguard-nonebot nginx || true
echo "迁移完成：应用目录 $NEW_DIR"
