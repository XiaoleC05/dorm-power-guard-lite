"""
注册 HTTP API 路由到 NoneBot
"""
from nonebot import get_driver, get_app
from nonebot.log import logger
from .http_api import router

# 获取驱动和应用实例
driver = get_driver()
app = get_app()

# 在应用启动时注册路由
@driver.on_startup
async def register_http_api():
    """注册 HTTP API 路由"""
    try:
        app.include_router(router, prefix="/api", tags=["HTTP API"])
        logger.info("✅ HTTP API 路由注册成功: /api/send_group_msg, /api/get_status")
    except Exception as e:
        logger.error(f"❌ HTTP API 路由注册失败：{e}")
