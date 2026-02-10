"""
测试 root 用户连接（尝试不同密码）
"""
import pymysql

def test_root_connection(password):
    """测试 root 用户连接"""
    try:
        print(f"正在尝试使用密码 '{password}' 连接...")
        connection = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password=password,
            charset='utf8mb4'
        )
        
        print(f"[成功] 密码 '{password}' 正确！")
        
        # 检查数据库是否存在
        with connection.cursor() as cursor:
            cursor.execute("SHOW DATABASES LIKE 'dorm_power_guard'")
            db_exists = cursor.fetchone()
            
            if db_exists:
                print("[成功] 数据库 'dorm_power_guard' 已存在")
            else:
                print("[警告] 数据库 'dorm_power_guard' 不存在，需要创建")
                print("执行以下SQL创建数据库：")
                print("CREATE DATABASE dorm_power_guard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        
        connection.close()
        return True
        
    except pymysql.err.OperationalError as e:
        error_code, error_msg = e.args
        if error_code == 1045:
            print(f"[失败] 密码 '{password}' 不正确")
        else:
            print(f"[错误] {error_msg}")
        return False
    except Exception as e:
        print(f"[错误] {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("测试 root 用户连接")
    print("=" * 60)
    print()
    
    # 尝试几个常见的密码
    passwords_to_try = ['783688', '', 'root', '123456']
    
    success = False
    for pwd in passwords_to_try:
        if test_root_connection(pwd):
            success = True
            print()
            print("=" * 60)
            print(f"正确的密码是: '{pwd}'")
            print("=" * 60)
            break
        print()
    
    if not success:
        print("=" * 60)
        print("所有测试密码都失败")
        print("请确认您的 MySQL root 密码")
        print("=" * 60)
