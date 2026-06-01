"""
GitHub Actions CI 入口脚本
只执行一次爬虫任务，不启动 Web 服务器
"""
import logging
import sys
import os

# 确保 backend 目录在 Python 路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    logger.info("=" * 60)
    logger.info("宿舍电费监控系统 - GitHub Actions 定时任务")
    logger.info("=" * 60)

    # 导入模块（需要在路径设置之后）
    from app.database import init_db, SessionLocal
    from app.services import CrawlerService

    # 初始化数据库表
    logger.info("正在初始化数据库...")
    try:
        init_db()
        logger.info("数据库初始化成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        logger.error("请检查数据库连接配置（DB_HOST, DB_USER, DB_PASSWORD 等）")
        return False

    # 执行爬虫任务
    logger.info("正在执行电费数据抓取...")
    db = SessionLocal()
    try:
        success = CrawlerService.crawl_and_save(db)
        if success:
            logger.info("电费数据抓取并保存成功")
            return True
        else:
            logger.warning("电费数据抓取完成，但部分或全部宿舍获取失败")
            return False
    except Exception as e:
        logger.error(f"爬虫任务执行失败: {e}", exc_info=True)
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
