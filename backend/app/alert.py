"""
告警模块（邮件、QQ机器人）
"""
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, Dict, List
from app.config import settings
from app.templates import get_email_template, get_email_text_template
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
    
    def send(self, dorm_number: str, category: str, category_name: str, 
             balance: float, threshold: float, 
             email_address: Optional[str] = None,
             kbalance: Optional[float] = None,
             zbalance: Optional[float] = None) -> bool:
        """
        发送邮件告警
        
        Args:
            dorm_number: 宿舍号
            category: 告警类别（ac/light）
            category_name: 告警类别名称（空调/照明）
            balance: 当前余量（度）
            threshold: 告警阈值（度）
            email_address: 接收邮箱地址（优先使用规则中的邮箱）
            kbalance: 空调余量（度，可选）
            zbalance: 照明余量（度，可选）
        """
        if not self.enabled:
            logger.info("邮件告警未启用")
            return False
        
        # 确定接收邮箱
        recipients = []
        if email_address:
            # 使用规则中配置的邮箱
            recipients = [email.strip() for email in email_address.split(',') if email.strip()]
        elif self.email_to:
            # 使用全局配置的邮箱
            recipients = self.email_to
        
        if not recipients:
            logger.error("未配置接收邮箱地址")
            return False
        
        if not all([self.smtp_host, self.smtp_user, self.smtp_password, self.email_from]):
            logger.error("邮件SMTP配置不完整")
            return False
        
        try:
            # 使用模板生成邮件内容
            subject, html_body = get_email_template(
                dorm_number=dorm_number,
                category=category,
                category_name=category_name,
                balance=balance,
                threshold=threshold,
                kbalance=kbalance,
                zbalance=zbalance
            )
            
            # 生成纯文本版本（备用）
            _, text_body = get_email_text_template(
                dorm_number=dorm_number,
                category=category,
                category_name=category_name,
                balance=balance,
                threshold=threshold,
                kbalance=kbalance,
                zbalance=zbalance
            )
            
            # 构建邮件
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_from
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            # 添加纯文本版本
            text_part = MIMEText(text_body, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # 添加HTML版本
            html_part = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 发送邮件
            if self.smtp_port == 465:
                # SSL端口，使用SMTP_SSL
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.email_from, recipients, msg.as_string())
                server.quit()
            else:
                # 普通端口，使用STARTTLS
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    if self.smtp_port == 587:
                        server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                    server.sendmail(self.email_from, recipients, msg.as_string())
            
            logger.info(f"邮件告警发送成功：{dorm_number}, {category_name}余量 {balance} 度, 发送至 {', '.join(recipients)}")
            return True
            
        except Exception as e:
            logger.error(f"邮件告警发送失败：{e}", exc_info=True)
            return False


class QQBotAlert:
    """QQ机器人告警"""
    
    def __init__(self):
        self.enabled = settings.QQ_BOT_ENABLED
        self.api_url = settings.QQ_BOT_API_URL
        self.group_id = settings.QQ_BOT_GROUP_ID
        self.user_id = settings.QQ_BOT_USER_ID
        self.bot_type = settings.QQ_BOT_TYPE
    
    def send(self, dorm_number: str, category: str, category_name: str,
             balance: float, threshold: float,
             kbalance: Optional[float] = None,
             zbalance: Optional[float] = None) -> bool:
        """
        发送QQ消息告警
        
        Args:
            dorm_number: 宿舍号
            category: 告警类别（ac/light）
            category_name: 告警类别名称（空调/照明）
            balance: 当前余量（度）
            threshold: 告警阈值（度）
            kbalance: 空调余量（度，可选）
            zbalance: 照明余量（度，可选）
        """
        if not self.enabled:
            logger.info("QQ告警未启用")
            return False
        
        if not self.api_url:
            logger.error("QQ机器人API地址未配置")
            return False
        
        try:
            message = f"【西华大学电费告警】\n"
            message += f"宿舍：{dorm_number}\n"
            message += f"告警类别：{category_name}\n"
            message += f"当前余量：{balance:.2f} 度\n"
            message += f"告警阈值：{threshold:.2f} 度\n"
            if kbalance is not None:
                message += f"空调余量：{kbalance:.2f} 度\n"
            if zbalance is not None:
                message += f"照明余量：{zbalance:.2f} 度\n"
            message += f"\n请及时充值，避免停电影响正常生活！"
            message += f"\n\n数据来源：西华大学一卡通宿舍用电小程序"
            message += f"\n管理员QQ：714085964"
            
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
                        logger.info(f"QQ告警发送成功：{dorm_number}, {category_name}余量 {balance} 度")
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
    
    def send_alert(self, dorm_number: str, category: str, category_name: str,
                   balance: float, threshold: float,
                   email_enabled: bool = False, 
                   email_address: Optional[str] = None,
                   qq_enabled: bool = False,
                   kbalance: Optional[float] = None,
                   zbalance: Optional[float] = None) -> Dict[str, bool]:
        """
        发送告警
        
        Args:
            dorm_number: 宿舍号
            category: 告警类别（ac/light）
            category_name: 告警类别名称（空调/照明）
            balance: 当前余量（度）
            threshold: 告警阈值（度）
            email_enabled: 是否启用邮件告警
            email_address: 接收邮箱地址
            qq_enabled: 是否启用QQ告警
            kbalance: 空调余量（度，可选）
            zbalance: 照明余量（度，可选）
        
        Returns:
            {'email': bool, 'qq': bool}
        """
        results = {'email': False, 'qq': False}
        
        if email_enabled:
            results['email'] = self.email_alert.send(
                dorm_number=dorm_number,
                category=category,
                category_name=category_name,
                balance=balance,
                threshold=threshold,
                email_address=email_address,
                kbalance=kbalance,
                zbalance=zbalance
            )
        
        if qq_enabled:
            results['qq'] = self.qq_alert.send(
                dorm_number=dorm_number,
                category=category,
                category_name=category_name,
                balance=balance,
                threshold=threshold,
                kbalance=kbalance,
                zbalance=zbalance
            )
        
        return results


def get_alert_manager() -> AlertManager:
    """获取告警管理器实例"""
    return AlertManager()
