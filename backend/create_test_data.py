"""
创建测试数据脚本
用于测试前端功能
"""
import sys
import os
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import PowerRecord
from app.schemas import PowerRecordCreate

def create_test_data():
    """创建测试数据"""
    db = SessionLocal()
    
    try:
        # 检查是否已有数据
        existing = db.query(PowerRecord).filter(
            PowerRecord.dorm_number == '101'
        ).first()
        
        if existing:
            print(f"宿舍101已有数据，最新余额: {existing.balance}元")
            print("如需重新创建测试数据，请先删除现有数据")
            return
        
        # 创建测试数据 - 最近30天的数据
        dorm_number = '101'
        base_balance = 50.0  # 起始余额
        records = []
        
        for i in range(30):
            # 每天递减0.5-2元
            balance = base_balance - (i * 1.5)
            if balance < 0:
                balance = 0
            
            record_time = datetime.now() - timedelta(days=30-i)
            
            record = PowerRecord(
                dorm_number=dorm_number,
                balance=round(balance, 2),
                power_consumption=round(5.0 + (i * 0.1), 2),
                record_time=record_time
            )
            records.append(record)
        
        db.add_all(records)
        db.commit()
        
        print(f"成功创建 {len(records)} 条测试数据")
        print(f"宿舍号: {dorm_number}")
        print(f"时间范围: {records[0].record_time.strftime('%Y-%m-%d')} 到 {records[-1].record_time.strftime('%Y-%m-%d')}")
        print(f"余额范围: {records[-1].balance}元 到 {records[0].balance}元")
        
    except Exception as e:
        db.rollback()
        print(f"创建测试数据失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("创建测试数据")
    print("=" * 60)
    print()
    create_test_data()
    print()
    print("=" * 60)
    print("完成！现在可以刷新前端页面查看数据")
    print("=" * 60)
