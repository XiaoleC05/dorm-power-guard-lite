"""
业务逻辑层
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
from typing import List, Optional
from app.models import PowerRecord, AlertRule, AlertLog
from app.schemas import PowerRecordCreate, AlertRuleCreate, AlertRuleUpdate
from app.crawler import get_crawler
from app.alert import get_alert_manager
import logging

logger = logging.getLogger(__name__)


class PowerRecordService:
    """电费记录服务"""
    
    @staticmethod
    def create_record(db: Session, record: PowerRecordCreate) -> PowerRecord:
        """创建电费记录"""
        db_record = PowerRecord(**record.dict())
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        return db_record
    
    @staticmethod
    def get_latest_record(db: Session, dorm_number: str) -> Optional[PowerRecord]:
        """获取最新的电费记录"""
        return db.query(PowerRecord).filter(
            PowerRecord.dorm_number == dorm_number
        ).order_by(desc(PowerRecord.record_time)).first()
    
    @staticmethod
    def get_records(db: Session, dorm_number: str, limit: int = 100) -> List[PowerRecord]:
        """获取电费记录列表"""
        return db.query(PowerRecord).filter(
            PowerRecord.dorm_number == dorm_number
        ).order_by(desc(PowerRecord.record_time)).limit(limit).all()
    
    @staticmethod
    def get_records_by_date_range(db: Session, dorm_number: str, 
                                   start_date: datetime, end_date: datetime) -> List[PowerRecord]:
        """按日期范围获取记录"""
        return db.query(PowerRecord).filter(
            PowerRecord.dorm_number == dorm_number,
            PowerRecord.record_time >= start_date,
            PowerRecord.record_time <= end_date
        ).order_by(desc(PowerRecord.record_time)).all()


class AlertRuleService:
    """告警规则服务"""
    
    @staticmethod
    def create_rule(db: Session, rule: AlertRuleCreate) -> AlertRule:
        """创建告警规则"""
        db_rule = AlertRule(**rule.dict())
        db.add(db_rule)
        db.commit()
        db.refresh(db_rule)
        return db_rule
    
    @staticmethod
    def get_rule(db: Session, dorm_number: str) -> Optional[AlertRule]:
        """获取告警规则"""
        return db.query(AlertRule).filter(
            AlertRule.dorm_number == dorm_number
        ).first()
    
    @staticmethod
    def get_all_rules(db: Session) -> List[AlertRule]:
        """获取所有告警规则"""
        return db.query(AlertRule).all()
    
    @staticmethod
    def update_rule(db: Session, dorm_number: str, rule_update: AlertRuleUpdate) -> Optional[AlertRule]:
        """更新告警规则"""
        rule = AlertRuleService.get_rule(db, dorm_number)
        if not rule:
            return None
        
        update_data = rule_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(rule, key, value)
        
        db.commit()
        db.refresh(rule)
        return rule
    
    @staticmethod
    def delete_rule(db: Session, dorm_number: str) -> bool:
        """删除告警规则"""
        rule = AlertRuleService.get_rule(db, dorm_number)
        if not rule:
            return False
        db.delete(rule)
        db.commit()
        return True


class AlertLogService:
    """告警日志服务"""
    
    @staticmethod
    def create_log(db: Session, dorm_number: str, balance: float, threshold: float,
                   alert_type: str, alert_status: str, alert_message: Optional[str] = None) -> AlertLog:
        """创建告警日志"""
        log = AlertLog(
            dorm_number=dorm_number,
            balance=balance,
            threshold=threshold,
            alert_type=alert_type,
            alert_status=alert_status,
            alert_message=alert_message
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
    
    @staticmethod
    def get_logs(db: Session, dorm_number: Optional[str] = None, limit: int = 50) -> List[AlertLog]:
        """获取告警日志"""
        query = db.query(AlertLog)
        if dorm_number:
            query = query.filter(AlertLog.dorm_number == dorm_number)
        return query.order_by(desc(AlertLog.created_at)).limit(limit).all()


class CrawlerService:
    """爬虫服务"""
    
    @staticmethod
    def crawl_and_save(db: Session) -> bool:
        """
        执行爬虫任务并保存数据
        返回是否成功
        """
        try:
            crawler = get_crawler()
            data = crawler.fetch_power_data()
            
            if not data:
                logger.warning("爬虫未获取到数据")
                return False
            
            # 保存记录
            record = PowerRecordCreate(**data)
            PowerRecordService.create_record(db, record)
            
            logger.info(f"成功抓取并保存电费数据：{data['dorm_number']}, 余额 {data['balance']} 元")
            
            # 检查是否需要告警
            CrawlerService.check_and_alert(db, data['dorm_number'], data['balance'])
            
            return True
            
        except Exception as e:
            logger.error(f"爬虫任务执行失败：{e}")
            return False
    
    @staticmethod
    def check_and_alert(db: Session, dorm_number: str, balance: float):
        """检查余额并触发告警"""
        rule = AlertRuleService.get_rule(db, dorm_number)
        
        if not rule or not rule.enabled:
            return
        
        if balance >= rule.threshold:
            return
        
        # 检查是否需要发送告警（避免频繁告警，至少间隔1小时）
        if rule.last_alert_time:
            time_diff = datetime.now() - rule.last_alert_time
            if time_diff < timedelta(hours=1):
                logger.info(f"距离上次告警不足1小时，跳过告警：{dorm_number}")
                return
        
        # 发送告警
        alert_manager = get_alert_manager()
        results = alert_manager.send_alert(
            dorm_number=dorm_number,
            balance=balance,
            threshold=rule.threshold,
            email_enabled=rule.email_enabled,
            qq_enabled=rule.qq_enabled
        )
        
        # 更新最后告警时间
        rule.last_alert_time = datetime.now()
        db.commit()
        
        # 记录告警日志
        for alert_type, success in results.items():
            if rule.email_enabled and alert_type == 'email':
                AlertLogService.create_log(
                    db, dorm_number, balance, rule.threshold,
                    'email', 'success' if success else 'failed'
                )
            if rule.qq_enabled and alert_type == 'qq':
                AlertLogService.create_log(
                    db, dorm_number, balance, rule.threshold,
                    'qq', 'success' if success else 'failed'
                )
        
        logger.info(f"告警检查完成：{dorm_number}, 余额 {balance} 元, 阈值 {rule.threshold} 元")
