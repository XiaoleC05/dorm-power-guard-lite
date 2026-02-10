"""
测试数据库连接脚本
用于诊断数据库连接问题
"""
import pymysql
import sys
from app.config import settings

def test_connection():
    """测试数据库连接"""
    print("=" * 60)
    print("数据库连接测试")
    print("=" * 60)
    print(f"主机: {settings.DB_HOST}")
    print(f"端口: {settings.DB_PORT}")
    print(f"用户: {settings.DB_USER}")
    print(f"数据库: {settings.DB_NAME}")
    print(f"密码: {'*' * len(settings.DB_PASSWORD)}")
    print("=" * 60)
    print()
    
    try:
        # 尝试连接数据库
        print("正在尝试连接数据库...")
        connection = pymysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
            charset='utf8mb4'
        )
        
        print("[成功] 数据库连接成功！")
        
        # 测试查询
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"MySQL 版本: {version[0]}")
            
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()
            print(f"当前数据库: {db_name[0]}")
            
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"现有表数量: {len(tables)}")
            if tables:
                print("现有表:")
                for table in tables:
                    print(f"  - {table[0]}")
        
        connection.close()
        print("\n[成功] 所有测试通过！数据库配置正确。")
        return True
        
    except pymysql.err.OperationalError as e:
        error_code, error_msg = e.args
        print(f"\n[错误] 数据库连接失败！")
        print(f"错误代码: {error_code}")
        print(f"错误信息: {error_msg}")
        print()
        
        if error_code == 1045:
            print("可能的原因：")
            print("1. 用户名或密码不正确")
            print("2. 用户不存在")
            print("3. 用户没有权限访问该数据库")
            print()
            print("解决方案：")
            print("1. 确认用户名和密码是否正确")
            print("2. 使用 root 用户登录 MySQL，检查用户是否存在：")
            print("   SELECT User, Host FROM mysql.user WHERE User='cxldatabase';")
            print("3. 如果用户不存在，创建用户并授权：")
            print(f"   CREATE USER 'cxldatabase'@'localhost' IDENTIFIED BY '783688';")
            print(f"   GRANT ALL PRIVILEGES ON dorm_power_guard.* TO 'cxldatabase'@'localhost';")
            print("   FLUSH PRIVILEGES;")
        elif error_code == 1049:
            print("可能的原因：数据库不存在")
            print(f"解决方案：创建数据库 {settings.DB_NAME}")
        elif error_code == 2003:
            print("可能的原因：MySQL 服务未启动或无法连接")
            print("解决方案：启动 MySQL 服务")
        
        return False
        
    except Exception as e:
        print(f"\n[错误] 发生未知错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
