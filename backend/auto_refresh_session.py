"""
自动刷新JSESSIONID脚本
定期访问API获取新的JSESSIONID并更新配置
"""
import sys
import os
import re
import logging
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
import urllib3
from app.config import settings

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def get_new_jsessionid():
    """获取新的JSESSIONID"""
    try:
        # 访问一个简单的API来获取新的JSESSIONID
        url = f"{settings.CRAWLER_BASE_URL}/channel/queryAreaList"
        params = {
            'factorycode': settings.CRAWLER_FACTORY_CODE or 'E014',
            'sign': '',
            'openid': settings.CRAWLER_OPENID,
            'orgid': settings.CRAWLER_ORG_ID or '2'
        }
        
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 16; V2408A Build/BQ2A.250705.001-BP2A.250605.031.A3_V000L1; wv) AppleWebKit/537.36',
            'Accept': '*/*',
        })
        
        response = session.get(url, params=params, verify=False, timeout=10)
        
        # 从响应Cookie中提取JSESSIONID
        if 'JSESSIONID' in session.cookies:
            new_jsessionid = session.cookies['JSESSIONID']
            logger.info(f"成功获取新的JSESSIONID: {new_jsessionid[:20]}...")
            return new_jsessionid
        else:
            logger.warning("响应中未找到JSESSIONID")
            return None
            
    except Exception as e:
        logger.error(f"获取JSESSIONID失败: {e}")
        return None


def update_env_file(new_jsessionid):
    """更新.env文件中的JSESSIONID"""
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换JSESSIONID
        pattern = r'CRAWLER_JSESSIONID=.*'
        replacement = f'CRAWLER_JSESSIONID={new_jsessionid}'
        
        new_content = re.sub(pattern, replacement, content)
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        logger.info("已更新.env文件中的JSESSIONID")
        return True
        
    except Exception as e:
        logger.error(f"更新.env文件失败: {e}")
        return False


def auto_refresh_session():
    """自动刷新JSESSIONID"""
    print("=" * 60)
    print(f"自动刷新JSESSIONID - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    if not settings.CRAWLER_OPENID:
        print("[错误] 未配置 openid，无法刷新JSESSIONID")
        return False
    
    print("正在获取新的JSESSIONID...")
    new_jsessionid = get_new_jsessionid()
    
    if new_jsessionid:
        print(f"[成功] 获取到新的JSESSIONID")
        print(f"  新值: {new_jsessionid[:30]}...")
        print()
        
        # 检查是否需要更新
        if new_jsessionid == settings.CRAWLER_JSESSIONID:
            print("[信息] JSESSIONID未变化，无需更新")
            return True
        
        print("正在更新配置文件...")
        if update_env_file(new_jsessionid):
            print()
            print("=" * 60)
            print("[成功] JSESSIONID已更新！")
            print("=" * 60)
            print()
            print("注意：需要重启后端服务才能生效")
            print("  停止服务：在运行服务的终端按 Ctrl+C")
            print("  重新启动：cd backend && python run.py")
            return True
        else:
            print("[失败] 更新配置文件失败")
            return False
    else:
        print("[失败] 未能获取新的JSESSIONID")
        return False


if __name__ == "__main__":
    try:
        auto_refresh_session()
    except Exception as e:
        print(f"[错误] 刷新失败: {e}")
        import traceback
        traceback.print_exc()
