"""
告警模块（邮件、QQ机器人）
"""
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class EmailAlert:
    """邮件告警"""
    
    def __init__(self):
        self.enabled = settings.EMAIL_ENABLED
        self.smtp_host = settings.EMAIL_SMTP_HOST
        self.smtp_port = settings.EMAIL_SMTP_PORT
        self.smtp_user = settings.EMAIL_SMTP_USER
        self.smtp_password = settings.EMAIL_SMTP_PASSWORD
        self.email_from = settings.EMAIL_FROM
        self.email_to = settings.EMAIL_TO.split(',') if settings.EMAIL_TO else []
    
    def send(self, dorm_number: str, balance: float, threshold: float) -> bool:
        """发送邮件告警"""
        if not self.enabled:
            logger.info("邮件告警未启用")
            return False
        
        if not all([self.smtp_host, self.smtp_user, self.smtp_password, self.email_from, self.email_to]):
            logger.error("邮件配置不完整")
            return False
        
        try:
            # 构建邮件内容
            subject = f"【电费告警】宿舍 {dorm_number} 电费余额不足"
            body = f"""
            宿舍电费监控系统告警
            
            宿舍号：{dorm_number}
            当前余额：{balance} 元
            告警阈值：{threshold} 元
            
            请及时充值，避免停电影响生活。
            """
            
            msg = MIMEMultipart()
            msg['From'] = self.email_from
            msg['To'] = ', '.join(self.email_to)
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 发送邮件
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"邮件告警发送成功：{dorm_number}, 余额 {balance} 元")
            return True
            
        except Exception as e:
            logger.error(f"邮件告警发送失败：{e}")
            return False


class QQBotAlert:
    """QQ机器人告警"""
    
    def __init__(self):
        self.enabled = settings.QQ_BOT_ENABLED
        self.api_url = settings.QQ_BOT_API_URL
        self.group_id = settings.QQ_BOT_GROUP_ID
        self.user_id = settings.QQ_BOT_USER_ID
        self.bot_type = settings.QQ_BOT_TYPE
    
    def send(self, dorm_number: str, balance: float, threshold: float) -> bool:
        """发送QQ消息告警"""
        if not self.enabled:
            logger.info("QQ告警未启用")
            return False
        
        if not self.api_url:
            logger.error("QQ机器人API地址未配置")
            return False
        
        try:
            message = f"【电费告警】\n宿舍：{dorm_number}\n当前余额：{balance} 元\n告警阈值：{threshold} 元\n请及时充值！"
            
            # 根据不同的机器人类型调用不同的API
            if self.bot_type == "go-cqhttp":
                # go-cqhttp API格式
                if self.group_id:
                    # 发送到群
                    url = f"{self.api_url}/send_group_msg"
                    data = {
                        "group_id": int(self.group_id),
                        "message": message
                    }
                elif self.user_id:
                    # 发送到私聊
                    url = f"{self.api_url}/send_private_msg"
                    data = {
                        "user_id": int(self.user_id),
                        "message": message
                    }
                else:
                    logger.error("QQ群号或用户ID未配置")
                    return False
                
                response = requests.post(url, json=data, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    if result.get("status") == "ok" or result.get("retcode") == 0:
                        logger.info(f"QQ告警发送成功：{dorm_number}, 余额 {balance} 元")
                        return True
                    else:
                        logger.error(f"QQ告警发送失败：{result}")
                        return False
                else:
                    logger.error(f"QQ告警API请求失败：{response.status_code}")
                    return False
            
            elif self.bot_type == "nonebot":
                # NoneBot API格式（需要根据实际API调整）
                logger.warning("NoneBot告警需要根据实际API实现")
                return False
            
            else:
                logger.error(f"不支持的QQ机器人类型：{self.bot_type}")
                return False
                
        except Exception as e:
            logger.error(f"QQ告警发送失败：{e}")
            return False


class AlertManager:
    """告警管理器"""
    
    def __init__(self):
        self.email_alert = EmailAlert()
        self.qq_alert = QQBotAlert()
    
    def send_alert(self, dorm_number: str, balance: float, threshold: float, 
                   email_enabled: bool = False, qq_enabled: bool = False) -> Dict[str, bool]:
        """
        发送告警
        返回：{'email': bool, 'qq': bool}
        """
        results = {'email': False, 'qq': False}
        
        if email_enabled:
            results['email'] = self.email_alert.send(dorm_number, balance, threshold)
        
        if qq_enabled:
            results['qq'] = self.qq_alert.send(dorm_number, balance, threshold)
        
        return results


def get_alert_manager() -> AlertManager:
    """获取告警管理器实例"""
    return AlertManager()
