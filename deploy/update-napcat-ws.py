#!/usr/bin/env python3
import glob
import json

WS_URL = "ws://127.0.0.1:8080/onebot/v11/ws"

for path in glob.glob("/opt/napcat/config/onebot11*.json"):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for client in data.get("network", {}).get("websocketClients", []):
        client["url"] = WS_URL
        client["enable"] = True
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"updated {path}")
