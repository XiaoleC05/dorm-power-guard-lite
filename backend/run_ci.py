"""
GitHub Actions CI 入口脚本
只执行一次爬虫任务，不启动 Web 服务器
"""
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def get_dorm_number() -> str:
    """从环境变量获取宿舍号"""
    return os.getenv("CRAWLER_DORM_NUMBER", "未知")


def main():
    logger.info("=" * 60)
    logger.info("宿舍电费监控系统 - GitHub Actions 定时任务")
    logger.info("=" * 60)

    from app.database import init_db, SessionLocal
    from app.services import CrawlerService, PowerRecordService
    from app.ci_notify import QQDirectNotifier

    notifier = QQDirectNotifier()
    dorm_number = get_dorm_number()

    logger.info("正在初始化数据库...")
    try:
        init_db()
        logger.info("数据库初始化成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        notifier.send_error(f"数据库初始化失败: {e}")
        return False

    logger.info("正在执行电费数据抓取...")
    db = SessionLocal()
    try:
        success = CrawlerService.crawl_and_save(db)

        if success:
            logger.info("电费数据抓取并保存成功")

            latest = PowerRecordService.get_latest_record(db, dorm_number)
            if latest:
                kbalance = latest.kbalance
                zbalance = latest.zbalance
                kpower = latest.kpower_consumption
                zpower = latest.zpower_consumption

                summary = (
                    f"抓取成功 | 空调: {kbalance or 'N/A'}度 "
                    f"照明: {zbalance or 'N/A'}度"
                )
                logger.info(summary)

                notifier.send_report(
                    dorm_number=dorm_number,
                    kbalance=kbalance,
                    zbalance=zbalance,
                    kpower=kpower,
                    zpower=zpower,
                )

                if (kbalance is not None and kbalance < 20) or \
                   (zbalance is not None and zbalance < 20):
                    logger.warning("电费余额低于 20 度，发送告警通知")
                    notifier.send_alert(
                        dorm_number=dorm_number,
                        kbalance=kbalance,
                        zbalance=zbalance,
                    )

            return True
        else:
            logger.warning("电费数据抓取完成，但部分或全部宿舍获取失败")
            notifier.send_error("电费数据抓取失败，请检查认证信息是否过期")
            return False

    except Exception as e:
        logger.error(f"爬虫任务执行失败: {e}", exc_info=True)
        notifier.send_error(str(e))
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
