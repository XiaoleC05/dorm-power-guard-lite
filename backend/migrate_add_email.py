"""
添加邮箱地址字段的迁移脚本
"""
import sys
import os
import pymysql
from app.config import settings

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def add_email_address_field():
    """添加邮箱地址字段"""
    print("=" * 70)
    print("数据库迁移 - 添加邮箱地址字段")
    print("=" * 70)
    print()
    
    try:
        connection = pymysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        # 检查字段是否存在
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'alert_rules' 
            AND COLUMN_NAME = 'email_address'
        """, (settings.DB_NAME,))
        
        if cursor.fetchone():
            print("[信息] email_address 字段已存在")
        else:
            # 添加字段
            cursor.execute("""
                ALTER TABLE alert_rules 
                ADD COLUMN email_address VARCHAR(255) NULL COMMENT '邮件告警接收邮箱地址' AFTER email_enabled
            """)
            connection.commit()
            print("[成功] 添加 email_address 字段")
        
        cursor.close()
        connection.close()
        
        print()
        print("=" * 70)
        print("[完成] 数据库迁移成功！")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"[错误] 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = add_email_address_field()
    sys.exit(0 if success else 1)
