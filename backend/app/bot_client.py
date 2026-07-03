"""NoneBot HTTP API 客户端辅助（鉴权头）。"""
from typing import Dict

from app.config import settings


def bot_api_headers() -> Dict[str, str]:
    headers = {"Content-Type": "application/json"}
    token = (settings.QQ_BOT_API_TOKEN or "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers
