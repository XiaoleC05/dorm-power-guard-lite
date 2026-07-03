#!/usr/bin/env bash
# 健康检查：后端、NoneBot、Nginx
set -euo pipefail

LOG_TAG="dorm-healthcheck"
FAIL=0
MSG=""

check() {
  local name="$1"
  shift
  if "$@"; then
    MSG+="[OK] $name "
  else
    MSG+="[FAIL] $name "
    FAIL=1
  fi
}

check_nonebot() {
  local body
  body=$(curl -fsS --max-time 10 http://127.0.0.1:8080/api/get_status) || return 1
  python3 -c "import json,sys; d=json.loads(sys.argv[1]); sys.exit(0 if d.get('status')=='ok' else 1)" "$body"
}

check "backend" curl -fsS --max-time 10 http://127.0.0.1:8000/health
check "nonebot" check_nonebot
check "nginx" systemctl is-active --quiet nginx

if [ "$FAIL" -ne 0 ]; then
  logger -t "$LOG_TAG" "$MSG"
  echo "UNHEALTHY: $MSG" >&2
  exit 1
fi

echo "HEALTHY: $MSG"
