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
        """创建电费记录，并计算用电量差值"""
        # 获取上次记录
        last_record = PowerRecordService.get_latest_record(db, record.dorm_number)
        
        # 计算用电量差值
        kpower_consumption = None
        zpower_consumption = None
        
        if last_record:
            # 计算空调用电量差值（当前值 - 上次值）
            if record.kbalance is not None and last_record.kbalance is not None:
                kpower_consumption = record.kbalance - last_record.kbalance
                # 如果差值为负，说明可能是充值了，设为None
                if kpower_consumption < 0:
                    kpower_consumption = None
            
            # 计算照明用电量差值（当前值 - 上次值）
            if record.zbalance is not None and last_record.zbalance is not None:
                zpower_consumption = record.zbalance - last_record.zbalance
                # 如果差值为负，说明可能是充值了，设为None
                if zpower_consumption < 0:
                    zpower_consumption = None
        
        # 创建记录
        record_dict = record.dict()
        record_dict['kpower_consumption'] = kpower_consumption
        record_dict['zpower_consumption'] = zpower_consumption
        
        db_record = PowerRecord(**record_dict)
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
                   alert_category: Optional[str], alert_type: str, alert_status: str, 
                   alert_message: Optional[str] = None) -> AlertLog:
        """创建告警日志"""
        log = AlertLog(
            dorm_number=dorm_number,
            alert_category=alert_category,
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
    def crawl_and_save(db: Session, force_alert: bool = False) -> bool:
        """
        执行爬虫任务并保存数据
        返回是否成功
        
        Args:
            db: 数据库会话
            force_alert: 是否强制发送告警（忽略防频繁告警限制，用于手动触发）
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
            
            logger.info(f"成功抓取并保存电费数据：{data['dorm_number']}, 空调余量 {data.get('kbalance', 'N/A')} 度, 照明余量 {data.get('zbalance', 'N/A')} 度")
            
            # 检查是否需要告警
            CrawlerService.check_and_alert(db, data['dorm_number'], data.get('kbalance'), data.get('zbalance'), force_alert=force_alert)
            
            return True
            
        except Exception as e:
            logger.error(f"爬虫任务执行失败：{e}")
            return False
    
    @staticmethod
    def check_and_alert(db: Session, dorm_number: str, kbalance: Optional[float] = None, zbalance: Optional[float] = None, force_alert: bool = False):
        """
        检查余量并触发告警（分别检查空调和照明）
        
        Args:
            db: 数据库会话
            dorm_number: 宿舍号
            kbalance: 空调余量
            zbalance: 照明余量
            force_alert: 是否强制发送告警（忽略防频繁告警限制）
        """
        rule = AlertRuleService.get_rule(db, dorm_number)
        
        if not rule or not rule.enabled:
            return
        
        # 检查空调告警
        if kbalance is not None and rule.kthreshold is not None:
            if kbalance < rule.kthreshold:
                CrawlerService._send_alert(
                    db, rule, dorm_number, kbalance, rule.kthreshold, 'ac', '空调', force_alert=force_alert
                )
        
        # 检查照明告警
        if zbalance is not None and rule.zthreshold is not None:
            if zbalance < rule.zthreshold:
                CrawlerService._send_alert(
                    db, rule, dorm_number, zbalance, rule.zthreshold, 'light', '照明', force_alert=force_alert
                )
        
        # 兼容旧版本：如果设置了threshold但没有设置kthreshold和zthreshold
        if rule.threshold is not None and rule.kthreshold is None and rule.zthreshold is None:
            balance = kbalance if kbalance is not None else zbalance
            if balance is not None and balance < rule.threshold:
                CrawlerService._send_alert(
                    db, rule, dorm_number, balance, rule.threshold, 'ac', '空调', force_alert=force_alert
                )
    
    @staticmethod
    def _send_alert(db: Session, rule: AlertRule, dorm_number: str, balance: float, 
                    threshold: float, category: str, category_name: str, force_alert: bool = False):
        """
        发送告警
        
        Args:
            db: 数据库会话
            rule: 告警规则
            dorm_number: 宿舍号
            balance: 当前余量
            threshold: 告警阈值
            category: 告警类别（ac/light）
            category_name: 告警类别名称（空调/照明）
            force_alert: 是否强制发送告警（忽略防频繁告警限制）
        """
        # 检查是否需要发送告警（避免频繁告警，至少间隔1小时）
        # 但如果是上次告警失败，或强制告警，则立即发送
        if not force_alert and rule.last_alert_time:
            time_diff = datetime.now() - rule.last_alert_time
            if time_diff < timedelta(hours=1):
                # 检查上次告警是否成功
                last_log = db.query(AlertLog).filter(
                    AlertLog.dorm_number == dorm_number,
                    AlertLog.alert_category == category
                ).order_by(desc(AlertLog.created_at)).first()
                
                # 如果上次告警成功，则跳过（避免频繁告警）
                if last_log and last_log.alert_status == 'success':
                    logger.info(f"距离上次成功告警不足1小时，跳过告警：{dorm_number} ({category_name})")
                    return
                # 如果上次告警失败，则立即重试
                elif last_log and last_log.alert_status == 'failed':
                    logger.info(f"上次告警失败，立即重试：{dorm_number} ({category_name})")
                else:
                    logger.info(f"距离上次告警不足1小时，跳过告警：{dorm_number} ({category_name})")
                    return
        
        # 获取当前最新的记录以获取完整的余量信息
        latest_record = PowerRecordService.get_latest_record(db, dorm_number)
        kbalance = latest_record.kbalance if latest_record else None
        zbalance = latest_record.zbalance if latest_record else None
        
        # 发送告警
        alert_manager = get_alert_manager()
        results = alert_manager.send_alert(
            dorm_number=dorm_number,
            category=category,
            category_name=category_name,
            balance=balance,
            threshold=threshold,
            email_enabled=rule.email_enabled,
            email_address=rule.email_address,
            qq_enabled=rule.qq_enabled,
            kbalance=kbalance,
            zbalance=zbalance
        )
        
        # 记录告警日志
        all_success = True
        for alert_type, success in results.items():
            if rule.email_enabled and alert_type == 'email':
                AlertLogService.create_log(
                    db, dorm_number, balance, threshold, category,
                    'email', 'success' if success else 'failed'
                )
                if not success:
                    all_success = False
            if rule.qq_enabled and alert_type == 'qq':
                AlertLogService.create_log(
                    db, dorm_number, balance, threshold, category,
                    'qq', 'success' if success else 'failed'
                )
                if not success:
                    all_success = False
        
        # 只有在至少有一个告警发送成功时，才更新最后告警时间
        # 如果全部失败，不更新时间，以便下次立即重试
        if all_success and (results.get('email') or results.get('qq')):
            rule.last_alert_time = datetime.now()
            db.commit()
            logger.info(f"告警发送成功：{dorm_number}, {category_name}余量 {balance} 度, 阈值 {threshold} 度")
        else:
            # 即使失败也提交日志记录
            db.commit()
            logger.warning(f"告警发送失败：{dorm_number}, {category_name}余量 {balance} 度, 阈值 {threshold} 度，将在下次检查时重试")
