#!/usr/bin/env bash
set -euo pipefail

NB_DIR="/opt/dorm-power-guard-lite/backend/nonebot_bot"
WS_URL="ws://127.0.0.1:8080/onebot/v11/ws"
COMPOSE_FILE="/opt/dorm-power-guard-lite/deploy/docker/napcat-compose.yml"

echo "[1] NoneBot .env (仅本机监听)"
mkdir -p "$NB_DIR"
cat > "$NB_DIR/.env" <<EOF
HOST=127.0.0.1
PORT=8080
EOF

echo "[2] Restart NoneBot"
systemctl restart dorm-nonebot
sleep 4

echo "[3] Update all NapCat onebot configs -> $WS_URL"
python3 - "$WS_URL" <<'PY'
import glob, json, sys
ws_url = sys.argv[1]
for path in glob.glob("/opt/napcat/config/onebot11*.json"):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for client in data.get("network", {}).get("websocketClients", []):
        client["url"] = ws_url
        client["enable"] = True
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"updated {path}")
PY

echo "[4] Recreate NapCat with host network"
docker stop napcat 2>/dev/null || true
docker rm napcat 2>/dev/null || true
if [ -f "$COMPOSE_FILE" ] && docker compose version >/dev/null 2>&1; then
  docker compose -f "$COMPOSE_FILE" up -d
else
  docker run -d \
    --name napcat \
    --restart unless-stopped \
    --network host \
    -v /opt/napcat/QQ:/app/.config/QQ \
    -v /opt/napcat/config:/app/napcat/config \
    ghcr.io/napneko/nodenapcat:latest
fi

sleep 15

echo "[5] Status"
curl -s http://127.0.0.1:8080/api/get_status || true
echo
docker logs napcat 2>&1 | strings | grep -iE 'connect|ws|onebot|online|1270667498|error|fail' | tail -15
