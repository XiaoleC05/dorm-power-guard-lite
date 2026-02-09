"""
Pydantic模型（API请求/响应模型）
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PowerRecordBase(BaseModel):
    dorm_number: str
    balance: float
    power_consumption: Optional[float] = None


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
    threshold: float
    enabled: bool = True
    email_enabled: bool = False
    qq_enabled: bool = False


class AlertRuleCreate(AlertRuleBase):
    pass


class AlertRuleUpdate(BaseModel):
    threshold: Optional[float] = None
    enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
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
    balance: float
    threshold: float
    alert_type: str
    alert_status: str
    alert_message: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
