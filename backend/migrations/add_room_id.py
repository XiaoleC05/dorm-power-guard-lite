"""
数据库迁移脚本：添加 room_id 字段到 alert_rules 表
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
    """添加 room_id 字段"""
    try:
        with engine.connect() as conn:
            # 检查字段是否已存在
            result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'alert_rules' 
                AND COLUMN_NAME = 'room_id'
            """))
            exists = result.scalar() > 0
            
            if exists:
                logger.info("字段 room_id 已存在，跳过迁移")
                return
            
            # 添加字段
            conn.execute(text("""
                ALTER TABLE alert_rules 
                ADD COLUMN room_id VARCHAR(50) NULL 
                COMMENT '房间ID（roomid，用于查询电费数据）' 
                AFTER dorm_number
            """))
            conn.commit()
            logger.info("✅ 成功添加字段 room_id")
            
            # 如果有320宿舍的规则，更新它的room_id（从.env配置中读取）
            # 注意：这里需要手动更新，因为.env中的值可能不同
            logger.info("提示：请手动更新320宿舍的room_id为5699（如果存在）")
            
    except Exception as e:
        logger.error(f"❌ 迁移失败：{e}", exc_info=True)
        raise


if __name__ == "__main__":
    upgrade()
