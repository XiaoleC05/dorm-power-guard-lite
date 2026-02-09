"""
定时任务调度器
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
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
    
    # 解析执行时间点
    hours = [int(h.strip()) for h in settings.SCHEDULER_HOURS.split(',') if h.strip()]
    
    if not hours:
        logger.warning("未配置定时任务执行时间，使用默认时间：8,12,18,22")
        hours = [8, 12, 18, 22]
    
    # 为每个时间点添加定时任务
    for hour in hours:
        scheduler.add_job(
            scheduled_crawl,
            trigger=CronTrigger(hour=hour, minute=0),  # 每天指定小时的第0分钟执行
            id=f'crawl_job_{hour}',
            name=f'电费爬虫任务-{hour}点',
            replace_existing=True
        )
        logger.info(f"已添加定时任务：每天 {hour}:00 执行爬虫")
    
    scheduler.start()
    logger.info("定时任务调度器已启动")


def shutdown_scheduler():
    """关闭调度器"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("定时任务调度器已关闭")
