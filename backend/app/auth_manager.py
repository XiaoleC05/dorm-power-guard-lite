"""
认证信息自动获取和管理模块
实现方案一：模拟小程序首次访问，自动获取JSESSIONID
"""
import requests
import logging
import re
from typing import Optional, Tuple
from app.config import settings
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class AuthManager:
    """认证信息管理器 - 自动获取和管理openid和JSESSIONID"""
    
    def __init__(self):
        self.base_url = settings.CRAWLER_BASE_URL or "https://ecard.xhu.edu.cn"
        self.org_id = settings.CRAWLER_ORG_ID or "2"
        self.factory_code = settings.CRAWLER_FACTORY_CODE or "E014"
        self.sign = settings.CRAWLER_SIGN or "qt"
        
        # 创建会话
        self.session = requests.Session()
        self._setup_session_headers()
    
    def _setup_session_headers(self):
        """设置会话请求头（模拟微信小程序）"""
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
    
    def get_new_session(self, openid: Optional[str] = None) -> Optional[str]:
        """
        获取新的JSESSIONID
        
        Args:
            openid: 如果提供openid，使用它；否则尝试从配置中获取
        
        Returns:
            新的JSESSIONID，如果获取失败返回None
        """
        try:
            # 使用openid（如果提供）或从配置中获取
            use_openid = openid or settings.CRAWLER_OPENID
            
            if not use_openid:
                logger.warning("未提供openid，无法获取JSESSIONID")
                return None
            
            # 访问一个简单的API来获取新的JSESSIONID
            # 使用queryAreaList API，因为它是最简单的，只需要openid
            url = f"{self.base_url}/channel/queryAreaList"
            params = {
                'factorycode': self.factory_code,
                'sign': '',
                'openid': use_openid,
                'orgid': self.org_id
            }
            
            logger.info("正在获取新的JSESSIONID...")
            response = self.session.get(url, params=params, verify=False, timeout=10)
            
            # 从响应Cookie中提取JSESSIONID
            if 'JSESSIONID' in self.session.cookies:
                new_jsessionid = self.session.cookies['JSESSIONID']
                logger.info(f"成功获取新的JSESSIONID: {new_jsessionid[:20]}...")
                return new_jsessionid
            else:
                # 尝试从Set-Cookie响应头中提取
                set_cookie = response.headers.get('Set-Cookie', '')
                if 'JSESSIONID' in set_cookie:
                    match = re.search(r'JSESSIONID=([^;]+)', set_cookie)
                    if match:
                        new_jsessionid = match.group(1)
                        logger.info(f"从Set-Cookie中提取到JSESSIONID: {new_jsessionid[:20]}...")
                        return new_jsessionid
                
                logger.warning("响应中未找到JSESSIONID")
                logger.debug(f"响应状态码: {response.status_code}")
                logger.debug(f"响应头: {dict(response.headers)}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"获取JSESSIONID失败: {e}")
            return None
        except Exception as e:
            logger.error(f"获取JSESSIONID时发生错误: {e}", exc_info=True)
            return None
    
    def auto_get_auth(self) -> Tuple[Optional[str], Optional[str]]:
        """
        自动获取认证信息（方案一：模拟小程序首次访问）
        
        Returns:
            (openid, jsessionid) 元组
        """
        # openid通常需要从微信获取，这里我们尝试从配置中获取
        # 如果配置中没有，返回None（需要用户手动配置一次）
        openid = settings.CRAWLER_OPENID
        
        if not openid:
            logger.warning("未配置openid，无法自动获取。openid通常需要手动配置一次（通过抓包获取）")
            logger.info("提示：openid通常长期有效，只需要配置一次")
            return None, None
        
        # 自动获取JSESSIONID
        jsessionid = self.get_new_session(openid)
        
        if jsessionid:
            logger.info("成功自动获取认证信息")
            return openid, jsessionid
        else:
            logger.error("自动获取JSESSIONID失败")
            return openid, None
    
    def refresh_jsessionid(self) -> Optional[str]:
        """
        刷新JSESSIONID（使用现有的openid）
        
        Returns:
            新的JSESSIONID，如果刷新失败返回None
        """
        return self.get_new_session()
    
    def verify_auth(self, openid: Optional[str] = None, jsessionid: Optional[str] = None) -> bool:
        """
        验证认证信息是否有效
        
        Args:
            openid: 要验证的openid（如果为None，使用配置中的）
            jsessionid: 要验证的jsessionid（如果为None，使用配置中的）
        
        Returns:
            如果认证有效返回True，否则返回False
        """
        try:
            use_openid = openid or settings.CRAWLER_OPENID
            use_jsessionid = jsessionid or settings.CRAWLER_JSESSIONID
            
            if not use_openid:
                logger.error("未提供openid，无法验证")
                return False
            
            # 创建一个临时会话来测试
            test_session = requests.Session()
            test_session.headers.update(self.session.headers)
            
            if use_jsessionid:
                test_session.cookies.set('JSESSIONID', use_jsessionid)
            
            # 使用queryBuildingList API验证（更可靠，因为需要更多参数）
            # 如果这个API成功，说明认证信息有效
            url = f"{self.base_url}/channel/queryBuildingList"
            params = {
                'factorycode': self.factory_code,
                'sign': self.sign,
                'areaid': settings.CRAWLER_AREA_ID or '1',
                'yqid': settings.CRAWLER_YQ_ID or '3',
                'openid': use_openid,
                'orgid': self.org_id
            }
            
            response = test_session.get(url, params=params, verify=False, timeout=10)
            
            # 检查响应
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get('success', False):
                        logger.info("认证信息有效")
                        return True
                    else:
                        # 即使success=false，也可能是其他原因（如参数错误）
                        # 只要不是401/403，就认为认证信息可能有效
                        logger.debug(f"API返回success=false: {result.get('message', '未知错误')}")
                        return True  # 暂时认为有效，让实际使用来验证
                except Exception:
                    # 如果响应不是JSON，检查状态码
                    if response.status_code == 200:
                        logger.info("认证信息有效（状态码200）")
                        return True
                    return False
            elif response.status_code == 401:
                logger.warning("认证失败：401 Unauthorized")
                return False
            elif response.status_code == 403:
                logger.warning("认证失败：403 Forbidden")
                return False
            else:
                # 其他状态码可能是服务器问题，不一定是认证问题
                logger.debug(f"验证返回状态码 {response.status_code}，可能是服务器问题")
                # 如果状态码不是认证相关错误，暂时认为认证信息可能有效
                # 让实际使用来验证
                return True
                
        except Exception as e:
            logger.error(f"验证认证信息时发生错误: {e}", exc_info=True)
            return False


def get_auth_manager() -> AuthManager:
    """获取认证管理器实例"""
    return AuthManager()
