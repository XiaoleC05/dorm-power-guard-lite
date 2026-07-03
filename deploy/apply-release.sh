#!/usr/bin/env bash
# 在服务器上应用已构建的发布包（GitHub Actions self-hosted 或手动执行）
set -euo pipefail

APP_DIR=/opt/DormGuard
OLD_APP_DIR=/opt/dorm-power-guard-lite
RELEASE_DIR="${1:-/tmp/dormguard-release}"

if [ ! -d "$RELEASE_DIR/backend" ]; then
  echo "错误：未找到 $RELEASE_DIR/backend，请先解压 dormguard-release.tar.gz"
  exit 1
fi

# 兼容旧部署路径：迁移 .env 与 venv
if [ -d "$OLD_APP_DIR" ]; then
  mkdir -p "$APP_DIR/backend"
  if [ -f "$OLD_APP_DIR/backend/.env" ] && [ ! -f "$APP_DIR/backend/.env" ]; then
    cp -a "$OLD_APP_DIR/backend/.env" "$APP_DIR/backend/.env"
  fi
  if [ -d "$OLD_APP_DIR/backend/venv" ] && [ ! -d "$APP_DIR/backend/venv" ]; then
    cp -a "$OLD_APP_DIR/backend/venv" "$APP_DIR/backend/venv"
  fi
fi

mkdir -p "$APP_DIR/backend" "$APP_DIR/frontend/dist" "$APP_DIR/deploy"
rsync -a "$RELEASE_DIR/backend/" "$APP_DIR/backend/"
rsync -a --delete "$RELEASE_DIR/frontend-dist/" "$APP_DIR/frontend/dist/"
rsync -a "$RELEASE_DIR/deploy/" "$APP_DIR/deploy/"
chmod +x "$APP_DIR/deploy/"*.sh "$APP_DIR/deploy/monitor/"*.sh 2>/dev/null || true

cd "$APP_DIR/backend"
if [ ! -d venv ]; then python3 -m venv venv; fi
./venv/bin/pip install --upgrade pip -q
./venv/bin/pip install -r requirements.txt -q
if [ -f requirements-nonebot.txt ]; then
  ./venv/bin/pip install -r requirements-nonebot.txt -q
fi

cp "$APP_DIR/deploy/systemd/dormguard-backend.service" /etc/systemd/system/
cp "$APP_DIR/deploy/systemd/dormguard-nonebot.service" /etc/systemd/system/
cp "$APP_DIR/deploy/systemd/dormguard-healthcheck.service" /etc/systemd/system/
cp "$APP_DIR/deploy/systemd/dormguard-healthcheck.timer" /etc/systemd/system/
cp "$APP_DIR/deploy/nginx/oxelia51.com.conf" /etc/nginx/sites-available/oxelia51.com
ln -sf /etc/nginx/sites-available/oxelia51.com /etc/nginx/sites-enabled/oxelia51.com
rm -f /etc/nginx/sites-enabled/masterc.cn

systemctl disable dorm-backend dorm-nonebot dorm-healthcheck.timer 2>/dev/null || true
rm -f /etc/systemd/system/dorm-backend.service /etc/systemd/system/dorm-nonebot.service
rm -f /etc/systemd/system/dorm-healthcheck.service /etc/systemd/system/dorm-healthcheck.timer

systemctl daemon-reload
systemctl enable --now dormguard-healthcheck.timer
systemctl restart dormguard-backend dormguard-nonebot
bash "$APP_DIR/deploy/fix-napcat.sh" || true
nginx -t
systemctl reload nginx
"$APP_DIR/deploy/monitor/dormguard-healthcheck.sh" || true
echo "Deploy success"
