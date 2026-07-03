#!/usr/bin/env bash
# 在服务器上轮换管理密码、JWT 密钥、NoneBot API Token
set -euo pipefail

ENV_FILE="${1:-/opt/DormGuard/backend/.env}"

if [ ! -f "$ENV_FILE" ]; then
  echo "找不到 $ENV_FILE"
  exit 1
fi

gen() { python3 -c "import secrets; print(secrets.token_urlsafe($1))"; }

ADMIN_PASSWORD="${ADMIN_PASSWORD:-$(gen 16)}"
ADMIN_JWT_SECRET="${ADMIN_JWT_SECRET:-$(gen 32)}"
QQ_BOT_API_TOKEN="${QQ_BOT_API_TOKEN:-$(gen 32)}"

upsert() {
  local key="$1" val="$2"
  if grep -q "^${key}=" "$ENV_FILE"; then
    sed -i "s|^${key}=.*|${key}=${val}|" "$ENV_FILE"
  else
    echo "${key}=${val}" >> "$ENV_FILE"
  fi
}

upsert APP_DEBUG false
upsert ADMIN_USERNAME root
upsert ADMIN_PASSWORD "$ADMIN_PASSWORD"
upsert ADMIN_JWT_SECRET "$ADMIN_JWT_SECRET"
upsert QQ_BOT_API_TOKEN "$QQ_BOT_API_TOKEN"

cp /opt/DormGuard/deploy/systemd/dormguard-nonebot.service /etc/systemd/system/ 2>/dev/null || true
systemctl daemon-reload
systemctl restart dormguard-backend dormguard-nonebot

echo "=== 已轮换密钥并重启服务 ==="
echo "ADMIN_USERNAME=root"
echo "ADMIN_PASSWORD=$ADMIN_PASSWORD"
echo "（JWT 与 Bot Token 已写入 .env，请勿泄露）"
echo ""
echo "请用新密码登录：https://oxelia51.com 或你的站点地址"
