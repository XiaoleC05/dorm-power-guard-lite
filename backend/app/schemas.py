"""
Pydantic模型（API请求/响应模型）
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PowerRecordBase(BaseModel):
    """电费记录基础模型"""
    dorm_number: str  # 宿舍号（如：320、324）
    balance: float  # 电费余量（度），主要监控项，通常是空调余量
    kbalance: Optional[float] = None  # 空调余量（度），从API获取的空调专用电费余量
    zbalance: Optional[float] = None  # 照明余量（度），从API获取的照明专用电费余量
    kpower_consumption: Optional[float] = None  # 空调用电量（度），与上次记录的差值
    zpower_consumption: Optional[float] = None  # 照明用电量（度），与上次记录的差值
    power_consumption: Optional[float] = None  # 用电量（度），已废弃，保留用于兼容性


class PowerRecordCreate(PowerRecordBase):
    pass


class PowerRecordResponse(PowerRecordBase):
    id: int
    record_time: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class AlertRuleBase(BaseModel):
    """告警规则基础模型"""
    dorm_number: str  # 宿舍号（如：320、324），唯一标识一个宿舍的告警规则
    room_id: Optional[str] = None  # 房间ID（roomid），从西华大学电费系统API获取，用于查询该宿舍的电费数据，多宿舍监控必需
    kthreshold: Optional[float] = None  # 空调告警阈值（度），当空调余量低于此值时触发告警
    zthreshold: Optional[float] = None  # 照明告警阈值（度），当照明余量低于此值时触发告警
    threshold: Optional[float] = None  # 告警阈值（度），已废弃，保留用于兼容性，请使用kthreshold和zthreshold
    enabled: bool = True  # 是否启用告警规则，False时不会触发任何告警
    email_enabled: bool = False  # 是否启用邮件告警，True时当余量低于阈值会发送邮件
    email_address: Optional[str] = None  # 邮件告警接收邮箱地址，启用邮件告警时必须填写
    qq_enabled: bool = False  # 是否启用QQ告警，True时当余量低于阈值会发送QQ消息
    qq_receiver_id: Optional[str] = None  # QQ告警接收者ID，可以是QQ号（私聊）或群号（群聊，通常>=1000000000），启用QQ告警时必须填写


class AlertRuleCreate(AlertRuleBase):
    pass


class AlertRuleUpdate(BaseModel):
    """告警规则更新模型，所有字段均为可选"""
    room_id: Optional[str] = None  # 房间ID（roomid），从西华大学电费系统API获取，用于查询该宿舍的电费数据
    kthreshold: Optional[float] = None  # 空调告警阈值（度），当空调余量低于此值时触发告警
    zthreshold: Optional[float] = None  # 照明告警阈值（度），当照明余量低于此值时触发告警
    threshold: Optional[float] = None  # 告警阈值（度），已废弃，保留用于兼容性
    enabled: Optional[bool] = None  # 是否启用告警规则
    email_enabled: Optional[bool] = None  # 是否启用邮件告警
    email_address: Optional[str] = None  # 邮件告警接收邮箱地址，启用邮件告警时必须填写
    qq_enabled: Optional[bool] = None  # 是否启用QQ告警
    qq_receiver_id: Optional[str] = None  # QQ告警接收者ID，可以是QQ号（私聊）或群号（群聊），启用QQ告警时必须填写


class AlertRuleResponse(AlertRuleBase):
    id: int
    last_alert_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AlertLogResponse(BaseModel):
    """告警日志响应模型"""
    id: int  # 主键ID
    dorm_number: str  # 宿舍号（如：320、324）
    alert_category: Optional[str] = None  # 告警类别：ac（空调）/light（照明），标识是哪个类型的电费余量触发了告警
    balance: float  # 触发告警时的余量（度）
    threshold: float  # 告警阈值（度）
    alert_type: str  # 告警类型：email（邮件告警）/qq（QQ告警）
    alert_status: str  # 告警状态：success（发送成功）/failed（发送失败）
    alert_message: Optional[str] = None  # 告警消息内容
    created_at: datetime  # 创建时间，告警发送的时间
    
    class Config:
        from_attributes = True
