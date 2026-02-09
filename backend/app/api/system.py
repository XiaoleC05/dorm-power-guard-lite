"""
系统管理API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import CrawlerService

router = APIRouter()


@router.post("/crawl", summary="手动触发爬虫任务")
async def manual_crawl(db: Session = Depends(get_db)):
    """手动触发一次爬虫任务"""
    success = CrawlerService.crawl_and_save(db)
    if success:
        return {"message": "爬虫任务执行成功"}
    else:
        return {"message": "爬虫任务执行失败", "success": False}
