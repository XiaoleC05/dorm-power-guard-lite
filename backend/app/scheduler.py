"""
定时任务调度器
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services import CrawlerService
from app.config import settings
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def scheduled_crawl():
    """定时爬虫任务"""
    logger.info("开始执行定时爬虫任务")
    db: Session = SessionLocal()
    try:
        CrawlerService.crawl_and_save(db)
    except Exception as e:
        logger.error(f"定时任务执行失败：{e}")
    finally:
        db.close()


def init_scheduler():
    """初始化调度器"""
    if scheduler.running:
        return
    
    # 每小时执行一次
    scheduler.add_job(
        scheduled_crawl,
        trigger=IntervalTrigger(hours=1),  # 每小时执行一次
        id='crawl_job_hourly',
        name='电费爬虫任务-每小时',
        replace_existing=True
    )
    logger.info("已添加定时任务：每小时执行一次爬虫")
    
    scheduler.start()
    logger.info("定时任务调度器已启动")


def shutdown_scheduler():
    """关闭调度器"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("定时任务调度器已关闭")
