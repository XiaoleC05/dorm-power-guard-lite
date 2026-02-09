"""
爬虫测试脚本
用于测试爬虫功能，方便调试
"""
import sys
import os
import logging

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.crawler import get_crawler
from app.config import settings

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_connection():
    """测试连接"""
    print("=" * 50)
    print("测试1: 连接测试")
    print("=" * 50)
    
    crawler = get_crawler()
    result = crawler.test_connection()
    print(f"连接测试结果: {'成功' if result else '失败'}")
    print()


def test_login():
    """测试登录"""
    print("=" * 50)
    print("测试2: 登录测试")
    print("=" * 50)
    
    crawler = get_crawler()
    print(f"Base URL: {crawler.base_url}")
    print(f"API Base URL: {crawler.api_base_url}")
    print(f"Token: {'已配置' if crawler.token else '未配置'}")
    print(f"Username: {crawler.username or '未配置'}")
    print(f"Dorm Number: {crawler.dorm_number or '未配置'}")
    print()
    
    result = crawler.login()
    print(f"登录结果: {'成功' if result else '失败'}")
    print()


def test_fetch_data():
    """测试数据抓取"""
    print("=" * 50)
    print("测试3: 数据抓取测试")
    print("=" * 50)
    
    crawler = get_crawler()
    data = crawler.fetch_power_data()
    
    if data:
        print("✅ 数据抓取成功！")
        print(f"宿舍号: {data.get('dorm_number')}")
        print(f"余额: {data.get('balance')} 元")
        print(f"用电量: {data.get('power_consumption', 'N/A')} 度")
        print()
        print("完整数据:")
        import json
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print("❌ 数据抓取失败")
        print("请检查:")
        print("1. Token是否配置正确")
        print("2. API地址是否正确")
        print("3. 网络连接是否正常")
        print("4. 查看上方日志了解详细错误信息")
    print()


def main():
    """主函数"""
    print("\n" + "=" * 50)
    print("宿舍电费爬虫测试工具")
    print("=" * 50 + "\n")
    
    # 检查配置
    if not settings.CRAWLER_DORM_NUMBER:
        print("⚠️  警告: 未配置宿舍号 (CRAWLER_DORM_NUMBER)")
        print()
    
    if not settings.CRAWLER_TOKEN and not settings.CRAWLER_USERNAME:
        print("⚠️  警告: 未配置Token或账号密码")
        print("请参考 CRAWLER_GUIDE.md 获取Token")
        print()
    
    # 运行测试
    try:
        test_connection()
        test_login()
        test_fetch_data()
    except KeyboardInterrupt:
        print("\n\n测试已中断")
    except Exception as e:
        print(f"\n\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)


if __name__ == "__main__":
    main()
