"""
Pydantic模型（API请求/响应模型）
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PowerRecordBase(BaseModel):
    dorm_number: str
    balance: float
    kbalance: Optional[float] = None  # 空调余量（度）
    zbalance: Optional[float] = None  # 照明余量（度）
    kpower_consumption: Optional[float] = None  # 空调用电量（度）
    zpower_consumption: Optional[float] = None  # 照明用电量（度）
    power_consumption: Optional[float] = None  # 已废弃


class PowerRecordCreate(PowerRecordBase):
    pass


class PowerRecordResponse(PowerRecordBase):
    id: int
    record_time: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class AlertRuleBase(BaseModel):
    dorm_number: str
    kthreshold: Optional[float] = None  # 空调告警阈值（度）
    zthreshold: Optional[float] = None  # 照明告警阈值（度）
    threshold: Optional[float] = None  # 已废弃，保留兼容性
    enabled: bool = True
    email_enabled: bool = False
    email_address: Optional[str] = None  # 邮件告警接收邮箱地址
    qq_enabled: bool = False


class AlertRuleCreate(AlertRuleBase):
    pass


class AlertRuleUpdate(BaseModel):
    kthreshold: Optional[float] = None  # 空调告警阈值（度）
    zthreshold: Optional[float] = None  # 照明告警阈值（度）
    threshold: Optional[float] = None  # 已废弃，保留兼容性
    enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    email_address: Optional[str] = None  # 邮件告警接收邮箱地址
    qq_enabled: Optional[bool] = None


class AlertRuleResponse(AlertRuleBase):
    id: int
    last_alert_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AlertLogResponse(BaseModel):
    id: int
    dorm_number: str
    alert_category: Optional[str] = None  # 告警类别：ac（空调）/light（照明）
    balance: float
    threshold: float
    alert_type: str
    alert_status: str
    alert_message: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
