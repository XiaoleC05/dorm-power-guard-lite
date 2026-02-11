"""
数据库迁移脚本：添加 qq_receiver_id 字段到 alert_rules 表
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def upgrade():
    """添加 qq_receiver_id 字段"""
    try:
        with engine.connect() as conn:
            # 检查字段是否已存在
            result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'alert_rules' 
                AND COLUMN_NAME = 'qq_receiver_id'
            """))
            exists = result.scalar() > 0
            
            if exists:
                logger.info("字段 qq_receiver_id 已存在，跳过迁移")
                return
            
            # 添加字段
            conn.execute(text("""
                ALTER TABLE alert_rules 
                ADD COLUMN qq_receiver_id VARCHAR(50) NULL 
                COMMENT 'QQ告警接收者QQ号（私聊）或群号（群聊）' 
                AFTER qq_enabled
            """))
            conn.commit()
            logger.info("✅ 成功添加字段 qq_receiver_id")
    except Exception as e:
        logger.error(f"❌ 迁移失败：{e}", exc_info=True)
        raise


if __name__ == "__main__":
    upgrade()
