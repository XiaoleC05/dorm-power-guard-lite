"""
CI 环境下的通知模块

支持多渠道推送：
1. PushPlus - 发送到微信
2. QMsg - 发送到 QQ 群 / QQ 号

通过环境变量控制启用哪些渠道：
- QQ_NOTIFY_API_KEY: (必填) PushPlus Token（微信推送）
- QQ_MSG_API_KEY: (可选) QMsg API Key，配置后启用 QQ 群推送
- QQ_GROUP_ID: (可选) QMsg 群号，配合 QQ_MSG_API_KEY 使用
"""
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


class PushPlusNotifier:
    """PushPlus 微信推送"""

    API_URL = "https://www.pushplus.plus/send"

    def __init__(self):
        self.token = os.getenv("QQ_NOTIFY_API_KEY", "")
        self.enabled = bool(self.token)

    def send(self, title: str, content: str) -> bool:
        if not self.enabled:
            return False
        try:
            import requests
            logger.info("正在通过 PushPlus 发送消息...")
            resp = requests.post(
                self.API_URL,
                json={"token": self.token, "title": title, "content": content},
                timeout=15,
            )
            result = resp.json()
            if result.get("code") == 200:
                logger.info("PushPlus 消息发送成功")
                return True
            else:
                logger.error(f"PushPlus 消息发送失败: {result}")
                return False
        except ImportError:
            logger.error("缺少 requests 库，无法发送 PushPlus 消息")
            return False
        except Exception as e:
            logger.error(f"PushPlus 发送异常: {e}")
            return False


class QQDirectNotifier:
    """QMsg QQ 群消息推送"""

    API_BASE = "https://qmsg.zendee.cn"

    def __init__(self):
        self.api_key = os.getenv("QQ_MSG_API_KEY", "")
        self.enabled = bool(self.api_key)
        self.group_id = os.getenv("QQ_GROUP_ID", "")

    def send(self, title: str, content: str) -> bool:
        if not self.enabled:
            return False
        try:
            import requests
            message = f"{title}\n{content}"
            url = f"{self.API_BASE}/send/{self.api_key}"
            data = {"msg": message}

            if self.group_id:
                data["qq"] = f"group:{self.group_id}"
                logger.info(f"正在通过 QMsg 发送消息到群 {self.group_id}...")
            else:
                logger.info("正在通过 QMsg 发送消息...")

            resp = requests.post(url, data=data, timeout=15)
            result = resp.json()

            if result.get("code") == 0 or result.get("success") is True:
                logger.info("QMsg 消息发送成功")
                return True
            else:
                logger.error(f"QMsg 消息发送失败: {result}")
                return False
        except ImportError:
            logger.error("缺少 requests 库，无法发送 QMsg 消息")
            return False
        except Exception as e:
            logger.error(f"QMsg 发送异常: {e}")
            return False


class Notifier:
    """
    组合通知器

    同时发送到所有已启用的渠道：
    - QQ_NOTIFY_API_KEY 配置了 → PushPlus（微信）
    - QQ_NOTIFY_API_KEY + QQ_GROUP_ID 都配置了 → QMsg（QQ 群）
    """

    def __init__(self):
        self.pushplus = PushPlusNotifier()
        self.qmsg = QQDirectNotifier()

    def send(self, title: str, content: str) -> bool:
        results = []
        if self.pushplus.enabled:
            results.append(self.pushplus.send(title, content))
        if self.qmsg.enabled and self.qmsg.group_id:
            results.append(self.qmsg.send(title, content))
        if not results:
            logger.info("未启用任何通知渠道")
            return False
        return all(results)

    def _build_content(self, dorm_number: str, kbalance=None, zbalance=None,
                       kpower=None, zpower=None, is_alert=False) -> str:
        if is_alert:
            content = (
                f"宿舍号：{dorm_number}\n"
                f"━━━━━━━━━━━━━━━━\n"
            )
            if kbalance is not None:
                content += f"空调余量：{kbalance:.2f} 度 ⚠️\n"
            if zbalance is not None:
                content += f"照明余量：{zbalance:.2f} 度 ⚠️\n"
            content += "\n请及时充值，避免停电！"
        else:
            content = (
                f"宿舍号：{dorm_number}\n"
                f"━━━━━━━━━━━━━━━━\n"
            )
            if kbalance is not None:
                content += f"空调余量：{kbalance:.2f} 度\n"
                if kpower is not None:
                    content += f"空调用电：{kpower:.2f} 度\n"
            if zbalance is not None:
                content += f"照明余量：{zbalance:.2f} 度\n"
                if zpower is not None:
                    content += f"照明用电：{zpower:.2f} 度\n"
        content += "\n数据来源：西华大学一卡通"
        return content

    def send_alert(self, dorm_number: str, kbalance: Optional[float] = None,
                   zbalance: Optional[float] = None) -> bool:
        title = "⚠️ 宿舍电费告警"
        content = self._build_content(dorm_number, kbalance, zbalance, is_alert=True)
        return self.send(title, content)

    def send_report(self, dorm_number: str, kbalance: Optional[float] = None,
                    zbalance: Optional[float] = None,
                    kpower: Optional[float] = None,
                    zpower: Optional[float] = None) -> bool:
        title = "📊 宿舍电费日报"
        content = self._build_content(dorm_number, kbalance, zbalance, kpower, zpower)
        return self.send(title, content)

    def send_error(self, error_msg: str) -> bool:
        title = "❌ 电费检测异常"
        content = f"检测任务执行失败：\n{error_msg}"
        return self.send(title, content)
