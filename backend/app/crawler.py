"""
电费数据爬虫模块 - 西华大学一卡通宿舍用电小程序

本模块用于抓取西华大学一卡通系统的宿舍电费数据。
管理员QQ：714085964
"""
import requests
from typing import Optional, Dict
from app.config import settings
from app.auth_manager import AuthManager
import logging
import json
import urllib3

# 禁用SSL警告（仅用于开发环境）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class PowerCrawler:
    """电费爬虫类 - 西华大学电费查询系统"""
    
    def __init__(self, auto_refresh_auth: bool = True):
        """
        初始化爬虫
        
        Args:
            auto_refresh_auth: 是否自动刷新认证信息（默认True）
        """
        self.base_url = settings.CRAWLER_BASE_URL or "https://ecard.xhu.edu.cn"
        self.room_id = settings.CRAWLER_ROOM_ID
        self.area_id = settings.CRAWLER_AREA_ID or "1"
        self.yq_id = settings.CRAWLER_YQ_ID or "3"
        self.building_id = settings.CRAWLER_BUILDING_ID or "40-1"
        self.floor_id = settings.CRAWLER_FLOOR_ID or "3"
        self.factory_code = settings.CRAWLER_FACTORY_CODE or "E014"
        self.sign = settings.CRAWLER_SIGN or "qt"
        self.org_id = settings.CRAWLER_ORG_ID or "2"
        self.dorm_number = settings.CRAWLER_DORM_NUMBER or "320"
        
        # 认证管理器
        self.auth_manager = AuthManager()
        
        # 自动获取认证信息（方案一：模拟小程序首次访问）
        if auto_refresh_auth:
            self.openid, self.jsessionid = self._auto_get_auth()
        else:
            # 使用配置中的认证信息
            self.openid = settings.CRAWLER_OPENID
            self.jsessionid = settings.CRAWLER_JSESSIONID
        
        self.session = requests.Session()
        # 设置请求头（模拟微信小程序）
        self.session.headers.update({
            'Host': 'ecard.xhu.edu.cn',
            'isWechatApp': 'true',
            'sec-ch-ua-platform': '"Android"',
            'session-type': 'uniapp',
            'sec-ch-ua': '"Chromium";v="142", "Android WebView";v="142", "Not_A Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'x-requested-with': 'XMLHttpRequest',
            'orgid': self.org_id,
            'User-Agent': 'Mozilla/5.0 (Linux; Android 16; V2408A Build/BQ2A.250705.001-BP2A.250605.031.A3_V000L1; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/142.0.7444.173 Mobile Safari/537.36 XWEB/1420229 MMWEBSDK/20260101 MMWEBID/6740 REV/04f9d4e638f33b1909b8f293dffa1cf978d8d0a3 MicroMessenger/8.0.68.3020(0x28004458) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64',
            'content-type': 'application/json',
            'Accept': '*/*',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': f'{self.base_url}/',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        })
        
        # 设置Cookie
        if self.jsessionid:
            self.session.cookies.set('JSESSIONID', self.jsessionid)
    
    def _auto_get_auth(self) -> tuple[Optional[str], Optional[str]]:
        """
        自动获取认证信息（方案一：模拟小程序首次访问）
        
        Returns:
            (openid, jsessionid) 元组
        """
        logger.info("正在自动获取认证信息（方案一：模拟小程序首次访问）...")
        openid, jsessionid = self.auth_manager.auto_get_auth()
        
        if openid and jsessionid:
            logger.info("成功自动获取认证信息")
            logger.debug(f"OpenID: {openid[:30]}...")
            logger.debug(f"JSESSIONID: {jsessionid[:20]}...")
        elif openid:
            logger.warning("已获取openid，但未能自动获取JSESSIONID，将使用配置中的JSESSIONID")
            jsessionid = settings.CRAWLER_JSESSIONID
        else:
            logger.warning("未能自动获取认证信息，将使用配置中的认证信息")
            openid = settings.CRAWLER_OPENID
            jsessionid = settings.CRAWLER_JSESSIONID
        
        return openid, jsessionid
    
    def login(self) -> bool:
        """
        登录验证（西华大学系统使用openid和JSESSIONID认证）
        如果认证信息无效，自动尝试刷新JSESSIONID
        """
        if not self.openid:
            logger.error("未配置openid，无法登录")
            return False
        
        # 验证当前认证信息是否有效
        if self.jsessionid:
            if self.auth_manager.verify_auth(self.openid, self.jsessionid):
                logger.info("认证信息有效，登录成功")
                return True
            else:
                logger.warning("当前JSESSIONID可能已过期，尝试自动刷新...")
                # 自动刷新JSESSIONID
                new_jsessionid = self.auth_manager.refresh_jsessionid()
                if new_jsessionid:
                    self.jsessionid = new_jsessionid
                    self.session.cookies.set('JSESSIONID', self.jsessionid)
                    logger.info("成功刷新JSESSIONID")
                    return True
                else:
                    logger.error("自动刷新JSESSIONID失败")
                    return False
        else:
            # 如果没有JSESSIONID，尝试自动获取
            logger.info("未配置JSESSIONID，尝试自动获取...")
            new_jsessionid = self.auth_manager.get_new_session(self.openid)
            if new_jsessionid:
                self.jsessionid = new_jsessionid
                self.session.cookies.set('JSESSIONID', self.jsessionid)
                logger.info("成功自动获取JSESSIONID")
                return True
            else:
                logger.warning("未能自动获取JSESSIONID，可能会影响请求")
                return True  # 仍然尝试继续（某些API可能不需要JSESSIONID）
    
    def fetch_power_data(self) -> Optional[Dict]:
        """
        抓取电费数据
        返回格式：{
            'dorm_number': '宿舍号',
            'balance': 余量（度，优先返回空调余量）,
            'kbalance': 空调余量（度）,
            'zbalance': 照明余量（度）,
            'power_consumption': 用电量（度，已废弃）
        }
        注意：用电量差值（kpower_consumption和zpower_consumption）在保存时自动计算
        """
        if not self.login():
            logger.error("登录失败，无法抓取数据")
            return None
        
        if not self.room_id:
            logger.error("未配置房间ID（CRAWLER_ROOM_ID），无法查询电费")
            return None
        
        try:
            logger.info(f"开始抓取房间 {self.dorm_number} (roomid={self.room_id}) 的电费数据")
            
            # 调用querySydl API查询电费
            api_url = f"{self.base_url}/channel/querySydl"
            
            params = {
                'areaid': self.area_id,
                'yqid': self.yq_id,
                'buildingid': self.building_id,
                'floorid': self.floor_id,
                'roomid': self.room_id,
                'factorycode': self.factory_code,
                'sign': self.sign,
                'openid': self.openid,
                'orgid': self.org_id,
            }
            
            logger.debug(f"请求URL: {api_url}")
            logger.debug(f"请求参数: {params}")
            
            # 禁用SSL验证（仅用于开发环境，生产环境应配置正确的证书）
            response = self.session.get(api_url, params=params, timeout=15, verify=False)
            response.raise_for_status()
            
            # 解析JSON响应
            result = response.json()
            logger.debug(f"API响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            # 检查响应是否成功
            if not result.get('success', False):
                error_msg = result.get('message', '未知错误')
                logger.error(f"API返回失败: {error_msg}")
                return None
            
            # 提取数据
            result_data = result.get('resultData', {})
            balance_list = result_data.get('balancelist', [])
            
            if not balance_list:
                logger.error("响应中未找到余额数据")
                return None
            
            # 获取第一条余额记录（通常只有一条）
            balance_info = balance_list[0]
            
            # 提取空调余额和照明余额
            kbalance_str = balance_info.get('kbalance', '0')  # 空调余额
            zbalance_str = balance_info.get('zbalance', '0')  # 照明余额
            
            # 转换为浮点数
            try:
                kbalance = float(kbalance_str)
                zbalance = float(zbalance_str)
            except (ValueError, TypeError) as e:
                logger.error(f"余额格式转换失败: {e}")
                return None
            
            # 优先返回空调余额（根据用户需求）
            balance = kbalance
            
            logger.info(f"成功获取电费数据 - 空调余量: {kbalance}度, 照明余量: {zbalance}度")
            
            return {
                'dorm_number': self.dorm_number,
                'balance': balance,  # 空调余额（主要监控项）
                'kbalance': kbalance,  # 空调余额
                'zbalance': zbalance,  # 照明余额
                'power_consumption': None  # 用电量（如果API有提供）
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"响应内容: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"抓取电费数据失败: {e}", exc_info=True)
            return None
    
    def test_connection(self) -> bool:
        """测试连接"""
        try:
            if not self.base_url:
                return False
            response = self.session.get(self.base_url, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"连接测试失败: {e}")
            return False


def get_crawler() -> PowerCrawler:
    """获取爬虫实例"""
    return PowerCrawler()
