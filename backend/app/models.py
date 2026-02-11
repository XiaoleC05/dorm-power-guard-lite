"""
数据库模型
"""
from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.database import Base


class PowerRecord(Base):
    """电费记录表"""
    __tablename__ = "power_records"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dorm_number = Column(String(50), nullable=False, comment="宿舍号")
    balance = Column(Float, nullable=False, comment="电费余量（度，主要监控项，通常是空调余量）")
    kbalance = Column(Float, nullable=True, comment="空调余量（度）")
    zbalance = Column(Float, nullable=True, comment="照明余量（度）")
    kpower_consumption = Column(Float, nullable=True, comment="空调用电量（度，与上次记录的差值）")
    zpower_consumption = Column(Float, nullable=True, comment="照明用电量（度，与上次记录的差值）")
    power_consumption = Column(Float, nullable=True, comment="用电量（度，已废弃，使用kpower_consumption和zpower_consumption）")
    record_time = Column(DateTime, nullable=False, server_default=func.now(), comment="记录时间")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    
    def __repr__(self):
        return f"<PowerRecord(id={self.id}, dorm={self.dorm_number}, balance={self.balance})>"


class AlertRule(Base):
    """告警规则表"""
    __tablename__ = "alert_rules"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dorm_number = Column(String(50), nullable=False, comment="宿舍号")
    room_id = Column(String(50), nullable=True, comment="房间ID（roomid，用于查询电费数据）")
    kthreshold = Column(Float, nullable=True, comment="空调告警阈值（度）")
    zthreshold = Column(Float, nullable=True, comment="照明告警阈值（度）")
    threshold = Column(Float, nullable=True, comment="告警阈值（度，已废弃，使用kthreshold和zthreshold）")
    enabled = Column(Boolean, default=True, nullable=False, comment="是否启用")
    email_enabled = Column(Boolean, default=False, nullable=False, comment="是否启用邮件告警")
    email_address = Column(String(255), nullable=True, comment="邮件告警接收邮箱地址")
    qq_enabled = Column(Boolean, default=False, nullable=False, comment="是否启用QQ告警")
    qq_receiver_id = Column(String(50), nullable=True, comment="QQ告警接收者QQ号（私聊）或群号（群聊）")
    last_alert_time = Column(DateTime, nullable=True, comment="最后告警时间")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<AlertRule(id={self.id}, dorm={self.dorm_number}, threshold={self.threshold})>"


class AlertLog(Base):
    """告警日志表（可选，用于记录告警历史）"""
    __tablename__ = "alert_logs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dorm_number = Column(String(50), nullable=False, comment="宿舍号")
    alert_category = Column(String(20), nullable=True, comment="告警类别：ac（空调）/light（照明）")
    balance = Column(Float, nullable=False, comment="触发告警时的余量（度）")
    threshold = Column(Float, nullable=False, comment="告警阈值（度）")
    alert_type = Column(String(20), nullable=False, comment="告警类型：email/qq")
    alert_status = Column(String(20), nullable=False, comment="告警状态：success/failed")
    alert_message = Column(Text, nullable=True, comment="告警消息")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    
    def __repr__(self):
        return f"<AlertLog(id={self.id}, dorm={self.dorm_number}, type={self.alert_type})>"
