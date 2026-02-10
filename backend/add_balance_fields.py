"""
添加空调余额和照明余额字段到数据库
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine
from sqlalchemy import text

def add_balance_fields():
    """添加kbalance和zbalance字段"""
    print("=" * 60)
    print("添加数据库字段")
    print("=" * 60)
    print()
    
    try:
        with engine.connect() as conn:
            # 检查字段是否已存在
            check_sql = """
            SELECT COUNT(*) as count
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'power_records'
            AND COLUMN_NAME IN ('kbalance', 'zbalance')
            """
            result = conn.execute(text(check_sql))
            count = result.fetchone()[0]
            
            if count >= 2:
                print("[信息] 字段 kbalance 和 zbalance 已存在")
                return
            
            # 添加kbalance字段
            try:
                conn.execute(text("""
                    ALTER TABLE power_records 
                    ADD COLUMN kbalance FLOAT NULL COMMENT '空调余额（元）' AFTER balance
                """))
                conn.commit()
                print("[成功] 已添加字段 kbalance")
            except Exception as e:
                if 'Duplicate column name' in str(e):
                    print("[信息] 字段 kbalance 已存在")
                else:
                    raise
            
            # 添加zbalance字段
            try:
                conn.execute(text("""
                    ALTER TABLE power_records 
                    ADD COLUMN zbalance FLOAT NULL COMMENT '照明余额（元）' AFTER kbalance
                """))
                conn.commit()
                print("[成功] 已添加字段 zbalance")
            except Exception as e:
                if 'Duplicate column name' in str(e):
                    print("[信息] 字段 zbalance 已存在")
                else:
                    raise
            
            print()
            print("=" * 60)
            print("字段添加完成！")
            print("=" * 60)
            
    except Exception as e:
        print(f"[错误] 添加字段失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_balance_fields()
