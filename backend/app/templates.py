"""
邮件通知模板 - 西华大学宿舍电费监控系统

奥泽莉亚工具箱 - 邮件模板
"""
from datetime import datetime
from typing import Optional


def get_email_template(dorm_number: str, category: str, category_name: str, 
                       balance: float, threshold: float, 
                       kbalance: Optional[float] = None, 
                       zbalance: Optional[float] = None) -> tuple[str, str]:
    """
    生成邮件通知模板
    
    Args:
        dorm_number: 宿舍号
        category: 告警类别（ac/light）
        category_name: 告警类别名称（空调/照明）
        balance: 当前余量（度）
        threshold: 告警阈值（度）
        kbalance: 空调余量（度，可选）
        zbalance: 照明余量（度，可选）
    
    Returns:
        (subject, html_body) 元组
    """
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 邮件主题
    subject = f"【西华大学电费告警】宿舍 {dorm_number} {category_name}余量不足"
    
    # 构建详细信息
    detail_info = ""
    if kbalance is not None:
        detail_info += f"<tr><td style='padding: 8px; border-bottom: 1px solid #eee;'>空调余量</td><td style='padding: 8px; border-bottom: 1px solid #eee;'><strong>{kbalance:.2f} 度</strong></td></tr>"
    if zbalance is not None:
        detail_info += f"<tr><td style='padding: 8px; border-bottom: 1px solid #eee;'>照明余量</td><td style='padding: 8px; border-bottom: 1px solid #eee;'><strong>{zbalance:.2f} 度</strong></td></tr>"
    
    # HTML邮件模板
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 600px;
            margin: 20px auto;
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #f56c6c 0%, #e6a23c 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
            font-weight: 500;
        }}
        .content {{
            padding: 30px;
        }}
        .alert-box {{
            background-color: #fff7e6;
            border-left: 4px solid #e6a23c;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .alert-box.warning {{
            background-color: #fff7e6;
            border-left-color: #e6a23c;
        }}
        .alert-box.danger {{
            background-color: #fef0f0;
            border-left-color: #f56c6c;
        }}
        .info-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        .info-table td {{
            padding: 12px;
            border-bottom: 1px solid #eee;
        }}
        .info-table td:first-child {{
            color: #666;
            width: 120px;
        }}
        .info-table td:last-child {{
            font-weight: 600;
            color: #333;
        }}
        .balance-value {{
            font-size: 20px;
            color: #f56c6c;
            font-weight: bold;
        }}
        .threshold-value {{
            font-size: 18px;
            color: #e6a23c;
            font-weight: bold;
        }}
        .footer {{
            background-color: #f5f5f5;
            padding: 20px;
            text-align: center;
            color: #999;
            font-size: 12px;
        }}
        .action-button {{
            display: inline-block;
            padding: 12px 24px;
            background-color: #409eff;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚠️ 西华大学电费告警通知</h1>
        </div>
        <div class="content">
            <div class="alert-box {'danger' if balance < threshold * 0.5 else 'warning'}">
                <h2 style="margin: 0 0 10px 0; color: #e6a23c;">{category_name}余量不足警告</h2>
                <p style="margin: 0; font-size: 16px;">
                    宿舍 <strong>{dorm_number}</strong> 的{category_name}余量已低于告警阈值，请及时充值！
                </p>
            </div>
            
            <table class="info-table">
                <tr>
                    <td>宿舍号</td>
                    <td><strong>{dorm_number}</strong></td>
                </tr>
                <tr>
                    <td>告警类别</td>
                    <td><strong>{category_name}</strong></td>
                </tr>
                <tr>
                    <td>当前余量</td>
                    <td><span class="balance-value">{balance:.2f} 度</span></td>
                </tr>
                <tr>
                    <td>告警阈值</td>
                    <td><span class="threshold-value">{threshold:.2f} 度</span></td>
                </tr>
                {detail_info}
                <tr>
                    <td>告警时间</td>
                    <td>{current_time}</td>
                </tr>
            </table>
            
            <div style="margin-top: 30px; padding: 15px; background-color: #f0f9ff; border-radius: 4px;">
                <h3 style="margin-top: 0; color: #409eff;">💡 温馨提示</h3>
                <ul style="margin: 10px 0; padding-left: 20px;">
                    <li>请尽快充值，避免停电影响正常生活</li>
                    <li>建议保持余量在安全范围内（建议 > {threshold * 1.5:.0f} 度）</li>
                    <li>系统将持续监控，余量恢复后将自动停止告警</li>
                    <li>数据来源：西华大学一卡通宿舍用电小程序</li>
                </ul>
            </div>
        </div>
        <div class="footer">
            <p><strong>西华大学宿舍电费监控系统</strong></p>
            <p>此邮件由系统自动发送，数据来源于西华大学一卡通系统</p>
            <p>如有疑问，请在告警群反馈（群号见系统配置）</p>
            <p style="margin-top: 10px; font-size: 11px; color: #bbb;">本系统仅用于学习和个人使用，请遵守西华大学相关规定</p>
        </div>
    </div>
</body>
</html>
    """
    
    return subject, html_body.strip()


def get_email_text_template(dorm_number: str, category: str, category_name: str,
                            balance: float, threshold: float,
                            kbalance: Optional[float] = None,
                            zbalance: Optional[float] = None) -> tuple[str, str]:
    """
    生成纯文本邮件通知模板（备用）
    
    Args:
        dorm_number: 宿舍号
        category: 告警类别（ac/light）
        category_name: 告警类别名称（空调/照明）
        balance: 当前余量（度）
        threshold: 告警阈值（度）
        kbalance: 空调余量（度，可选）
        zbalance: 照明余量（度，可选）
    
    Returns:
        (subject, text_body) 元组
    """
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    subject = f"【西华大学电费告警】宿舍 {dorm_number} {category_name}余量不足"
    
    text_body = f"""
西华大学宿舍电费监控系统告警通知

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ {category_name}余量不足警告

宿舍号：{dorm_number}
告警类别：{category_name}
当前余量：{balance:.2f} 度
告警阈值：{threshold:.2f} 度
"""
    
    if kbalance is not None:
        text_body += f"空调余量：{kbalance:.2f} 度\n"
    if zbalance is not None:
        text_body += f"照明余量：{zbalance:.2f} 度\n"
    
    text_body += f"""
告警时间：{current_time}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 温馨提示：
- 请尽快充值，避免停电影响正常生活
- 建议保持余量在安全范围内（建议 > {threshold * 1.5:.0f} 度）
- 系统将持续监控，余量恢复后将自动停止告警
- 数据来源：西华大学一卡通宿舍用电小程序

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

西华大学宿舍电费监控系统
此邮件由系统自动发送，数据来源于西华大学一卡通系统
如有疑问，请在告警群反馈（群号见系统配置）

本系统仅用于学习和个人使用，请遵守西华大学相关规定
    """
    
    return subject, text_body.strip()
