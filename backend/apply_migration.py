"""
应用数据库迁移脚本
添加用电量字段和告警阈值字段
"""
import sys
import os
import pymysql
from app.config import settings

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def apply_migration():
    """应用数据库迁移"""
    print("=" * 70)
    print("数据库迁移 - 添加用电量字段和告警阈值字段")
    print("=" * 70)
    print()
    
    try:
        # 连接数据库
        connection = pymysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        print("【步骤1】检查并添加 power_records 表的字段")
        print("-" * 70)
        
        # 检查字段是否存在
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'power_records' 
            AND COLUMN_NAME IN ('kpower_consumption', 'zpower_consumption')
        """, (settings.DB_NAME,))
        
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        # 添加空调用电量字段
        if 'kpower_consumption' not in existing_columns:
            cursor.execute("""
                ALTER TABLE power_records 
                ADD COLUMN kpower_consumption FLOAT NULL COMMENT '空调用电量（度，与上次记录的差值）' AFTER zbalance
            """)
            print("[成功] 添加 kpower_consumption 字段")
        else:
            print("[信息] kpower_consumption 字段已存在")
        
        # 添加照明用电量字段
        if 'zpower_consumption' not in existing_columns:
            cursor.execute("""
                ALTER TABLE power_records 
                ADD COLUMN zpower_consumption FLOAT NULL COMMENT '照明用电量（度，与上次记录的差值）' AFTER kpower_consumption
            """)
            print("[成功] 添加 zpower_consumption 字段")
        else:
            print("[信息] zpower_consumption 字段已存在")
        
        # 修改字段注释
        try:
            cursor.execute("""
                ALTER TABLE power_records 
                MODIFY COLUMN kbalance FLOAT NULL COMMENT '空调余量（度）'
            """)
            cursor.execute("""
                ALTER TABLE power_records 
                MODIFY COLUMN zbalance FLOAT NULL COMMENT '照明余量（度）'
            """)
            cursor.execute("""
                ALTER TABLE power_records 
                MODIFY COLUMN balance FLOAT NOT NULL COMMENT '电费余量（度，主要监控项，通常是空调余量）'
            """)
            print("[成功] 更新字段注释")
        except Exception as e:
            print(f"[警告] 更新字段注释时出错（可能已更新）: {e}")
        
        print()
        print("【步骤2】检查并添加 alert_rules 表的字段")
        print("-" * 70)
        
        # 检查告警规则表的字段
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'alert_rules' 
            AND COLUMN_NAME IN ('kthreshold', 'zthreshold')
        """, (settings.DB_NAME,))
        
        existing_alert_columns = [row[0] for row in cursor.fetchall()]
        
        # 添加空调阈值字段
        if 'kthreshold' not in existing_alert_columns:
            cursor.execute("""
                ALTER TABLE alert_rules 
                ADD COLUMN kthreshold FLOAT NULL COMMENT '空调告警阈值（度）' AFTER dorm_number
            """)
            print("[成功] 添加 kthreshold 字段")
            
            # 迁移旧的threshold值到kthreshold
            cursor.execute("""
                UPDATE alert_rules 
                SET kthreshold = threshold 
                WHERE kthreshold IS NULL AND threshold IS NOT NULL
            """)
            print("[成功] 迁移旧的threshold值到kthreshold")
        else:
            print("[信息] kthreshold 字段已存在")
        
        # 添加照明阈值字段
        if 'zthreshold' not in existing_alert_columns:
            cursor.execute("""
                ALTER TABLE alert_rules 
                ADD COLUMN zthreshold FLOAT NULL COMMENT '照明告警阈值（度）' AFTER kthreshold
            """)
            print("[成功] 添加 zthreshold 字段")
        else:
            print("[信息] zthreshold 字段已存在")
        
        # 修改threshold字段为可空
        try:
            cursor.execute("""
                ALTER TABLE alert_rules 
                MODIFY COLUMN threshold FLOAT NULL COMMENT '告警阈值（度，已废弃，使用kthreshold和zthreshold）'
            """)
            print("[成功] 修改threshold字段为可空")
        except Exception as e:
            print(f"[警告] 修改threshold字段时出错（可能已更新）: {e}")
        
        print()
        print("【步骤3】检查并添加 alert_logs 表的字段")
        print("-" * 70)
        
        # 检查告警日志表的字段
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'alert_logs' 
            AND COLUMN_NAME = 'alert_category'
        """, (settings.DB_NAME,))
        
        if cursor.fetchone() is None:
            cursor.execute("""
                ALTER TABLE alert_logs 
                ADD COLUMN alert_category VARCHAR(20) NULL COMMENT '告警类别：ac（空调）/light（照明）' AFTER dorm_number
            """)
            print("[成功] 添加 alert_category 字段")
        else:
            print("[信息] alert_category 字段已存在")
        
        # 修改字段注释
        try:
            cursor.execute("""
                ALTER TABLE alert_logs 
                MODIFY COLUMN balance FLOAT NOT NULL COMMENT '触发告警时的余量（度）'
            """)
            cursor.execute("""
                ALTER TABLE alert_logs 
                MODIFY COLUMN threshold FLOAT NOT NULL COMMENT '告警阈值（度）'
            """)
            print("[成功] 更新告警日志字段注释")
        except Exception as e:
            print(f"[警告] 更新告警日志字段注释时出错（可能已更新）: {e}")
        
        # 提交更改
        connection.commit()
        
        print()
        print("=" * 70)
        print("[完成] 数据库迁移成功！")
        print("=" * 70)
        
    except Exception as e:
        print(f"[错误] 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        if 'connection' in locals():
            connection.rollback()
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
    
    return True

if __name__ == "__main__":
    success = apply_migration()
    sys.exit(0 if success else 1)
