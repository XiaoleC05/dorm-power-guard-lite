"""
电费数据爬虫模块 - 针对微信小程序API抓取
"""
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict
from app.config import settings
import logging
import json
import re

logger = logging.getLogger(__name__)


class PowerCrawler:
    """电费爬虫类 - 支持小程序API调用"""
    
    def __init__(self):
        self.base_url = settings.CRAWLER_BASE_URL or "https://ecard.xhu.edu.cn"
        self.api_base_url = settings.CRAWLER_API_BASE_URL or f"{self.base_url}/api"
        self.token = settings.CRAWLER_TOKEN
        self.username = settings.CRAWLER_USERNAME
        self.password = settings.CRAWLER_PASSWORD
        self.dorm_number = settings.CRAWLER_DORM_NUMBER
        self.token_refresh_url = settings.CRAWLER_TOKEN_REFRESH_URL
        
        self.session = requests.Session()
        # 模拟小程序请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/78.0.3904.108 Mobile Safari/537.36 MicroMessenger/7.0.20.1781',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Content-Type': 'application/json',
            'Referer': f'{self.base_url}/',
            'Origin': self.base_url
        })
        
        # 如果有token，设置认证头
        if self.token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}',
                # 或者可能是其他格式，如：
                # 'token': self.token,
                # 'X-Auth-Token': self.token,
            })
    
    def login(self) -> bool:
        """
        登录系统（小程序场景）
        对于微信小程序，通常使用Token认证，不需要传统登录
        如果配置了Token，直接返回True
        如果没有Token，尝试通过账号密码获取Token
        """
        # 如果已有Token，验证Token是否有效
        if self.token:
            logger.info("使用配置的Token进行认证")
            # 可以尝试调用一个简单的API验证Token
            return self._verify_token()
        
        # 如果没有Token，尝试通过账号密码获取
        if self.username and self.password:
            logger.info(f"尝试通过账号密码获取Token：{self.username}")
            return self._get_token_by_login()
        
        logger.error("未配置Token或账号密码，无法登录")
        return False
    
    def _verify_token(self) -> bool:
        """验证Token是否有效"""
        try:
            # 尝试调用一个简单的API接口验证Token
            # 这里需要根据实际API调整
            test_url = f"{self.api_base_url}/user/info"  # 示例接口
            response = self.session.get(test_url, timeout=10)
            
            if response.status_code == 200:
                logger.info("Token验证成功")
                return True
            elif response.status_code == 401:
                logger.warning("Token已过期，需要刷新")
                return self._refresh_token()
            else:
                logger.warning(f"Token验证失败，状态码：{response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Token验证异常：{e}")
            return False
    
    def _get_token_by_login(self) -> bool:
        """
        通过账号密码获取Token
        注意：微信小程序通常不支持账号密码登录，这个方法可能需要根据实际情况调整
        """
        try:
            # 示例：调用登录API获取Token
            login_url = f"{self.api_base_url}/auth/login"
            login_data = {
                'username': self.username,
                'password': self.password
            }
            
            response = self.session.post(login_url, json=login_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                # 根据实际API响应格式提取Token
                # 可能的格式：
                # - result['data']['token']
                # - result['token']
                # - result['access_token']
                token = result.get('data', {}).get('token') or result.get('token')
                
                if token:
                    self.token = token
                    self.session.headers.update({'Authorization': f'Bearer {token}'})
                    logger.info("登录成功，已获取Token")
                    return True
                else:
                    logger.error("登录响应中未找到Token")
                    return False
            else:
                logger.error(f"登录失败，状态码：{response.status_code}, 响应：{response.text}")
                return False
                
        except Exception as e:
            logger.error(f"登录异常：{e}")
            return False
    
    def _refresh_token(self) -> bool:
        """刷新Token"""
        if not self.token_refresh_url:
            logger.warning("未配置Token刷新URL，无法刷新Token")
            return False
        
        try:
            response = self.session.post(self.token_refresh_url, timeout=10)
            if response.status_code == 200:
                result = response.json()
                new_token = result.get('data', {}).get('token') or result.get('token')
                if new_token:
                    self.token = new_token
                    self.session.headers.update({'Authorization': f'Bearer {new_token}'})
                    logger.info("Token刷新成功")
                    return True
            return False
        except Exception as e:
            logger.error(f"Token刷新失败：{e}")
            return False
    
    def fetch_power_data(self) -> Optional[Dict]:
        """
        抓取电费数据（小程序API方式）
        返回格式：{
            'dorm_number': '宿舍号',
            'balance': 余额（元）,
            'power_consumption': 用电量（度，可选）
        }
        """
        if not self.login():
            logger.error("登录失败，无法抓取数据")
            return None
        
        try:
            logger.info(f"开始抓取宿舍 {self.dorm_number} 的电费数据")
            
            # 方式1：直接调用小程序API（推荐）
            # 需要根据实际API接口调整URL和参数
            api_url = f"{self.api_base_url}/power/query"
            
            # 可能的API调用方式：
            # 1. GET请求带参数
            params = {
                'dorm': self.dorm_number,
                # 或其他参数名，如：'room', 'roomNumber', 'dormNumber'
            }
            response = self.session.get(api_url, params=params, timeout=15)
            
            # 2. 如果是POST请求
            # data = {'dorm_number': self.dorm_number}
            # response = self.session.post(api_url, json=data, timeout=15)
            
            response.raise_for_status()
            
            # 解析JSON响应
            result = response.json()
            
            # 根据实际API响应格式提取数据
            # 可能的响应格式示例：
            # {
            #   "code": 200,
            #   "data": {
            #     "balance": 50.0,
            #     "power": 100.5,
            #     "dorm": "101"
            #   }
            # }
            
            # 提取数据（需要根据实际响应结构调整）
            data = result.get('data', result)  # 有些API直接返回数据，有些在data字段中
            
            balance = self._extract_balance(data)
            power_consumption = self._extract_power_consumption(data)
            
            if balance is None:
                logger.error("未能从API响应中提取到余额信息")
                logger.debug(f"API响应：{json.dumps(result, ensure_ascii=False, indent=2)}")
                return None
            
            return {
                'dorm_number': self.dorm_number,
                'balance': balance,
                'power_consumption': power_consumption
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败：{e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"响应内容：{e.response.text}")
            return None
        except Exception as e:
            logger.error(f"抓取电费数据失败：{e}", exc_info=True)
            return None
    
    def _extract_balance(self, data: Dict) -> Optional[float]:
        """从响应数据中提取余额"""
        # 尝试多种可能的字段名
        balance_keys = ['balance', '余额', 'amount', 'money', 'fee', 'remaining', 'remain']
        
        for key in balance_keys:
            if key in data:
                value = data[key]
                # 转换为浮点数
                if isinstance(value, (int, float)):
                    return float(value)
                elif isinstance(value, str):
                    # 提取数字（去除"元"等字符）
                    numbers = re.findall(r'\d+\.?\d*', value.replace(',', ''))
                    if numbers:
                        return float(numbers[0])
        
        return None
    
    def _extract_power_consumption(self, data: Dict) -> Optional[float]:
        """从响应数据中提取用电量"""
        power_keys = ['power', 'powerConsumption', 'consumption', '用电量', '电量', 'kwh']
        
        for key in power_keys:
            if key in data:
                value = data[key]
                if isinstance(value, (int, float)):
                    return float(value)
                elif isinstance(value, str):
                    numbers = re.findall(r'\d+\.?\d*', value.replace(',', ''))
                    if numbers:
                        return float(numbers[0])
        
        return None
    
    def test_connection(self) -> bool:
        """测试连接"""
        try:
            if not self.base_url:
                return False
            response = self.session.get(self.base_url, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"连接测试失败：{e}")
            return False


def get_crawler() -> PowerCrawler:
    """获取爬虫实例"""
    return PowerCrawler()
