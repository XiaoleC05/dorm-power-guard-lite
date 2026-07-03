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

check "backend" curl -fsS --max-time 10 http://127.0.0.1:8000/health
check "nonebot" curl -fsS --max-time 10 http://127.0.0.1:8080/api/get_status
check "nginx" systemctl is-active --quiet nginx

if [ "$FAIL" -ne 0 ]; then
  logger -t "$LOG_TAG" "$MSG"
  echo "UNHEALTHY: $MSG" >&2
  exit 1
fi

echo "HEALTHY: $MSG"
