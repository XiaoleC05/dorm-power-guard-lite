"""
删除数据库中多余表的Python脚本

此脚本会自动检测数据库中所有表，并删除不在代码中定义的表。
当前代码中定义的表：
  1. power_records - 电费记录表
  2. alert_rules - 告警规则表
  3. alert_logs - 告警日志表

使用方法：
    python backend/scripts/db/drop_unused_tables.py
"""
import sys
import os
import io
import argparse
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError

# 设置Windows控制台编码为UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加backend目录到路径
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, backend_dir)

# 切换到backend目录（这样.env文件才能被正确读取）
os.chdir(backend_dir)

from app.config import settings
from app.database import DATABASE_URL

# 代码中定义的表（必须保留）
REQUIRED_TABLES = {
    'power_records',
    'alert_rules',
    'alert_logs'
}


def get_all_tables(engine):
    """获取数据库中所有表名"""
    inspector = inspect(engine)
    return set(inspector.get_table_names())


def drop_unused_tables(auto_confirm=False):
    """删除数据库中多余的表
    
    Args:
        auto_confirm: 如果为True，自动确认删除，不需要用户输入
    """
    print("=" * 60)
    print("删除数据库中多余的表")
    print("=" * 60)
    print()
    
    # 创建数据库引擎
    try:
        engine = create_engine(DATABASE_URL)
        print(f"[OK] 成功连接到数据库: {settings.DB_NAME}")
    except Exception as e:
        print(f"[ERROR] 连接数据库失败: {e}")
        return False
    
    # 获取所有表
    try:
        all_tables = get_all_tables(engine)
        print(f"[OK] 找到 {len(all_tables)} 个表")
    except Exception as e:
        print(f"[ERROR] 获取表列表失败: {e}")
        return False
    
    # 显示所有表
    print()
    print("数据库中的所有表：")
    for table in sorted(all_tables):
        marker = "[保留]" if table in REQUIRED_TABLES else "[删除]"
        print(f"  {marker} {table}")
    
    # 找出多余的表
    unused_tables = all_tables - REQUIRED_TABLES
    
    if not unused_tables:
        print()
        print("=" * 60)
        print("[OK] 没有多余的表需要删除！")
        print("=" * 60)
        return True
    
    print()
    print("=" * 60)
    print(f"发现 {len(unused_tables)} 个多余的表：")
    print("=" * 60)
    for table in sorted(unused_tables):
        print(f"  - {table}")
    
    print()
    print("警告：这些表将被永久删除！")
    
    if not auto_confirm:
        response = input("确认删除？(yes/no): ").strip().lower()
        if response != 'yes':
            print("操作已取消")
            return False
    else:
        print("[自动确认] 将自动删除这些表...")
    
    # 删除多余的表
    print()
    print("开始删除多余的表...")
    print("-" * 60)
    
    with engine.connect() as conn:
        # 禁用外键检查
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        conn.commit()
        
        success_count = 0
        failed_tables = []
        
        for table in sorted(unused_tables):
            try:
                conn.execute(text(f"DROP TABLE IF EXISTS `{table}`"))
                conn.commit()
                print(f"[OK] 已删除表: {table}")
                success_count += 1
            except SQLAlchemyError as e:
                print(f"[ERROR] 删除表失败 {table}: {e}")
                failed_tables.append(table)
        
        # 恢复外键检查
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        conn.commit()
    
    print("-" * 60)
    print()
    print("=" * 60)
    print("删除操作完成")
    print("=" * 60)
    print(f"成功删除: {success_count} 个表")
    if failed_tables:
        print(f"删除失败: {len(failed_tables)} 个表")
        for table in failed_tables:
            print(f"  - {table}")
    
    # 显示剩余的表
    print()
    print("剩余的表：")
    try:
        remaining_tables = get_all_tables(engine)
        for table in sorted(remaining_tables):
            print(f"  [保留] {table}")
    except Exception as e:
        print(f"[ERROR] 获取剩余表失败: {e}")
    
    return len(failed_tables) == 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='删除数据库中多余的表')
    parser.add_argument('-y', '--yes', action='store_true', 
                       help='自动确认删除，不需要用户输入')
    args = parser.parse_args()
    
    try:
        success = drop_unused_tables(auto_confirm=args.yes)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
