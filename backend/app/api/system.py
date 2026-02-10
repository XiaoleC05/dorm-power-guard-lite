"""
系统管理API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import CrawlerService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/crawl", summary="手动触发爬虫任务")
async def manual_crawl(db: Session = Depends(get_db)):
    """手动触发一次爬虫任务，重新获取最新余额数据"""
    try:
        logger.info("收到手动触发爬虫任务请求")
        # 手动触发时，强制发送告警（忽略防频繁告警限制）
        success = CrawlerService.crawl_and_save(db, force_alert=True)
        if success:
            return {
                "success": True,
                "message": "数据获取成功，已更新最新余额"
            }
        else:
            return {
                "success": False,
                "message": "数据获取失败，请检查网络连接和认证信息"
            }
    except Exception as e:
        logger.error(f"手动触发爬虫任务异常：{e}")
        return {
            "success": False,
            "message": f"数据获取异常：{str(e)}"
        }
