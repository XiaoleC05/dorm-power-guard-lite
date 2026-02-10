"""
配置文件 - 西华大学宿舍电费监控系统

本项目针对西华大学一卡通宿舍用电小程序。
管理员QQ：714085964
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # 数据库配置
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "dorm_power_guard"
    
    # 爬虫配置
    CRAWLER_BASE_URL: Optional[str] = None  # 电费查询网站地址（如：https://ecard.xhu.edu.cn）
    CRAWLER_API_BASE_URL: Optional[str] = None  # API基础地址（小程序API地址，如：https://ecard.xhu.edu.cn/api）
    CRAWLER_TOKEN: Optional[str] = None  # 认证Token（通过抓包获取）
    CRAWLER_USERNAME: Optional[str] = None  # 登录用户名（备用）
    CRAWLER_PASSWORD: Optional[str] = None  # 登录密码（备用）
    CRAWLER_DORM_NUMBER: Optional[str] = None  # 宿舍号
    CRAWLER_TOKEN_REFRESH_URL: Optional[str] = None  # Token刷新接口（如果需要）
    
    # 西华大学电费系统特定配置
    CRAWLER_OPENID: Optional[str] = None  # openid（通过抓包获取）
    CRAWLER_JSESSIONID: Optional[str] = None  # JSESSIONID（Cookie，通过抓包获取）
    CRAWLER_ROOM_ID: Optional[str] = None  # 房间ID（roomid）
    CRAWLER_AREA_ID: Optional[str] = "1"  # 区域ID（areaid，1=郫都校区）
    CRAWLER_YQ_ID: Optional[str] = "3"  # 园区ID（yqid，3=德馨苑）
    CRAWLER_BUILDING_ID: Optional[str] = "40-1"  # 楼栋ID（buildingid，40-1=3号楼小号-1单元）
    CRAWLER_FLOOR_ID: Optional[str] = "3"  # 楼层ID（floorid，3=3层）
    CRAWLER_FACTORY_CODE: Optional[str] = "E014"  # 工厂代码（factorycode）
    CRAWLER_SIGN: Optional[str] = "qt"  # 签名（sign）
    CRAWLER_ORG_ID: Optional[str] = "2"  # 组织ID（orgid）
    
    # 定时任务配置
    SCHEDULER_HOURS: str = "8,12,18,22"  # 每天执行时间点（小时）
    
    # 邮件配置
    EMAIL_ENABLED: bool = False
    EMAIL_SMTP_HOST: Optional[str] = None
    EMAIL_SMTP_PORT: int = 587
    EMAIL_SMTP_USER: Optional[str] = None
    EMAIL_SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[str] = None
    EMAIL_TO: Optional[str] = None  # 多个邮箱用逗号分隔
    
    # QQ机器人配置
    QQ_BOT_ENABLED: bool = False
    QQ_BOT_TYPE: Optional[str] = None  # go-cqhttp, nonebot等
    QQ_BOT_API_URL: Optional[str] = None  # QQ机器人API地址
    QQ_BOT_GROUP_ID: Optional[str] = None  # 群号
    QQ_BOT_USER_ID: Optional[str] = None  # 用户QQ号
    
    # 默认告警阈值
    DEFAULT_ALERT_THRESHOLD: float = 20.0  # 默认余额低于20元时告警
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
