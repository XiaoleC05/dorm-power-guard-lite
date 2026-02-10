"""
设置监控脚本 - 创建告警规则并启动监控
"""
import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.services import AlertRuleService
from app.schemas import AlertRuleCreate
from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def setup_monitoring():
    """设置监控规则"""
    print("=" * 60)
    print("设置监控规则")
    print("=" * 60)
    print()
    
    db = SessionLocal()
    
    try:
        dorm_number = settings.CRAWLER_DORM_NUMBER or "320"
        threshold = settings.DEFAULT_ALERT_THRESHOLD or 20.0
        
        print(f"宿舍号: {dorm_number}")
        print(f"告警阈值: {threshold}元")
        print()
        
        # 检查是否已存在规则
        existing = AlertRuleService.get_rule(db, dorm_number)
        
        if existing:
            print(f"[信息] 告警规则已存在")
            print(f"  阈值: {existing.threshold}元")
            print(f"  启用状态: {'已启用' if existing.enabled else '未启用'}")
            print()
            
            # 如果未启用，启用它
            if not existing.enabled:
                from app.schemas import AlertRuleUpdate
                update_data = AlertRuleUpdate(enabled=True)
                AlertRuleService.update_rule(db, dorm_number, update_data)
                print("[成功] 已启用告警规则")
            else:
                print("[信息] 告警规则已启用")
        else:
            # 创建新规则
            print("创建告警规则...")
            rule_data = AlertRuleCreate(
                dorm_number=dorm_number,
                threshold=threshold,
                enabled=True,
                email_enabled=False,
                qq_enabled=False
            )
            
            rule = AlertRuleService.create_rule(db, rule_data)
            print(f"[成功] 告警规则创建成功！")
            print(f"  宿舍号: {rule.dorm_number}")
            print(f"  阈值: {rule.threshold}元")
            print(f"  启用状态: {'已启用' if rule.enabled else '未启用'}")
        
        print()
        print("=" * 60)
        print("监控设置完成！")
        print("=" * 60)
        print()
        print("说明:")
        print("1. 定时任务会在每天8点、12点、18点、22点自动抓取数据")
        print("2. 当余额低于阈值时，系统会自动记录告警日志")
        print("3. 可以通过前端界面查看监控数据和告警日志")
        print()
        print("注意:")
        print("- 当前认证信息可能已过期（返回401错误）")
        print("- 请重新抓包获取新的openid和JSESSIONID")
        print("- 更新backend/.env文件后重启后端服务")
        
    except Exception as e:
        print(f"[错误] 设置失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    setup_monitoring()
