"""
HTTP API 插件：仅提供群消息发送（机器人 QQ 1270667498 固定，由 NapCat 登录）。
"""
import os
import secrets
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from nonebot import get_bot
from nonebot.log import logger

router = APIRouter()


def _verify_api_token(authorization: Optional[str] = Header(None)) -> None:
    """校验 Bearer Token；未配置 QQ_BOT_API_TOKEN 时仅记录警告（兼容迁移期）。"""
    expected = (os.environ.get("QQ_BOT_API_TOKEN") or "").strip()
    if not expected:
        logger.warning("QQ_BOT_API_TOKEN 未配置，HTTP API 处于无鉴权状态")
        return
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="缺少 API Token")
    token = authorization[7:].strip()
    if not secrets.compare_digest(token, expected):
        raise HTTPException(status_code=403, detail="无效 API Token")


@router.post("/send_group_msg")
async def send_group_msg(
    request: Request,
    _: None = Depends(_verify_api_token),
):
    """发送群消息 API"""
    try:
        data = await request.json()
        group_id = data.get("group_id")
        message = data.get("message")

        if not group_id or not message:
            raise HTTPException(status_code=400, detail="缺少必要参数：group_id 或 message")

        bot = get_bot()
        await bot.send_group_msg(group_id=int(group_id), message=str(message))

        logger.info(f"成功发送群消息：群号={group_id}, 消息={message[:50]}...")
        return {"status": "ok", "retcode": 0, "data": None}
    except Exception as e:
        logger.error(f"发送群消息失败：{e}")
        return JSONResponse(
            status_code=500,
            content={"status": "failed", "retcode": -1, "msg": str(e)},
        )


@router.get("/get_status")
async def get_status(_: None = Depends(_verify_api_token)):
    """获取机器人状态"""
    try:
        bot = get_bot()
        return {
            "status": "ok",
            "retcode": 0,
            "data": {
                "online": True,
                "bot_id": str(bot.self_id) if hasattr(bot, "self_id") else None,
            },
        }
    except ValueError as e:
        error_msg = str(e)
        if "no bots" in error_msg.lower() or "There are no bots" in error_msg:
            error_msg = "NoneBot未连接NapCatQQ，请启动NapCatQQ并连接到NoneBot"
        logger.warning(f"获取机器人状态失败：{error_msg}")
        return JSONResponse(
            status_code=200,
            content={"status": "failed", "retcode": -1, "msg": error_msg},
        )
    except Exception as e:
        logger.error(f"获取机器人状态异常：{e}", exc_info=True)
        return JSONResponse(
            status_code=200,
            content={"status": "failed", "retcode": -1, "msg": str(e)},
        )
