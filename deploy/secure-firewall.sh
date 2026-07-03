#!/usr/bin/env bash
# 收紧防火墙：仅开放 80/443；SSH 限制来源 IP
set -euo pipefail

SSH_ALLOW_IPS=(
  "218.200.225.186/32"
  "100.104.0.0/16"
)

if ! command -v ufw >/dev/null 2>&1; then
  apt-get update -qq
  apt-get install -y ufw
fi

ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 80/tcp
ufw allow 443/tcp
for cidr in "${SSH_ALLOW_IPS[@]}"; do
  ufw allow from "$cidr" to any port 22 proto tcp
done
ufw --force enable
ufw status verbose

echo "提示：8000/8080/6099 不应在阿里云安全组中对外开放"
