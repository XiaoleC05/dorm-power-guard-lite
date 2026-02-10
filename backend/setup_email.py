"""
交互式邮件配置脚本
"""
import os
import re
from pathlib import Path

def validate_email(email):
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_auth_code(code):
    """验证授权码格式（QQ邮箱授权码通常是16位）"""
    return len(code) >= 10 and len(code) <= 20

def update_env_file(env_path, updates):
    """更新.env文件"""
    if not os.path.exists(env_path):
        print(f"[错误] 找不到文件: {env_path}")
        return False
    
    # 读取文件内容
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 更新配置
    updated_lines = []
    for line in lines:
        updated = False
        for key, value in updates.items():
            if line.strip().startswith(f'{key}='):
                updated_lines.append(f'{key}={value}\n')
                updated = True
                break
        if not updated:
            updated_lines.append(line)
    
    # 写入文件
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)
    
    return True

def main():
    print("=" * 70)
    print("QQ邮箱配置向导")
    print("=" * 70)
    print()
    print("本脚本将帮助您配置QQ邮箱发送告警邮件功能")
    print()
    
    # 获取.env文件路径
    env_path = Path(__file__).parent / '.env'
    
    print("当前配置的发件邮箱: 1270667498@qq.com")
    print()
    
    # 获取授权码
    print("=" * 70)
    print("步骤1: 获取QQ邮箱授权码")
    print("=" * 70)
    print()
    print("请按照以下步骤获取授权码：")
    print("  1. 登录QQ邮箱：https://mail.qq.com")
    print("  2. 点击右上角'设置' -> '账户'")
    print("  3. 找到'POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务'部分")
    print("  4. 开启'POP3/SMTP服务'或'IMAP/SMTP服务'")
    print("  5. 点击'生成授权码'按钮")
    print("  6. 按提示发送短信后获取16位授权码")
    print()
    
    auth_code = input("请输入QQ邮箱授权码（16位）: ").strip()
    
    if not auth_code:
        print("[错误] 未输入授权码")
        return False
    
    if not validate_auth_code(auth_code):
        print("[警告] 授权码格式可能不正确（通常是16位），是否继续？(y/n): ", end='')
        confirm = input().strip().lower()
        if confirm != 'y':
            return False
    
    print()
    print("=" * 70)
    print("步骤2: 配置接收邮箱（可选）")
    print("=" * 70)
    print()
    print("告警邮件将发送到告警规则中配置的邮箱")
    print("如果告警规则中未配置，将使用以下默认邮箱")
    print()
    
    default_email = input("请输入默认接收邮箱（留空跳过）: ").strip()
    
    # 更新配置
    updates = {
        'EMAIL_ENABLED': 'true',
        'EMAIL_SMTP_HOST': 'smtp.qq.com',
        'EMAIL_SMTP_PORT': '465',
        'EMAIL_SMTP_USER': '1270667498@qq.com',
        'EMAIL_SMTP_PASSWORD': auth_code,
        'EMAIL_FROM': '1270667498@qq.com',
    }
    
    if default_email:
        if validate_email(default_email):
            updates['EMAIL_TO'] = default_email
        else:
            print("[警告] 邮箱格式不正确，将跳过默认接收邮箱配置")
    
    print()
    print("=" * 70)
    print("更新配置文件...")
    print("=" * 70)
    
    if update_env_file(env_path, updates):
        print("[成功] 配置文件已更新")
        print()
        print("配置摘要：")
        print(f"  发件邮箱: {updates['EMAIL_SMTP_USER']}")
        print(f"  SMTP服务器: {updates['EMAIL_SMTP_HOST']}")
        print(f"  SMTP端口: {updates['EMAIL_SMTP_PORT']}")
        if 'EMAIL_TO' in updates:
            print(f"  默认接收邮箱: {updates['EMAIL_TO']}")
        else:
            print(f"  默认接收邮箱: （未配置，将使用告警规则中的邮箱）")
        print()
        print("=" * 70)
        print("配置完成！")
        print("=" * 70)
        print()
        print("下一步：")
        print("  1. 运行测试脚本测试邮件发送: python test_email.py")
        print("  2. 或重启后端服务，系统将自动使用新配置")
        print()
        return True
    else:
        print("[错误] 更新配置文件失败")
        return False

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n配置已取消")
    except Exception as e:
        print(f"\n[错误] 配置过程中发生错误: {e}")
