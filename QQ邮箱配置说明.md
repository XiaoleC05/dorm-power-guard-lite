# QQ邮箱发送告警邮件配置说明

## 功能说明

本系统支持使用QQ邮箱作为发件邮箱，将告警邮件发送到指定的接收邮箱。告警邮件会发送到：
1. **告警规则中配置的邮箱**（优先级最高）
2. 如果规则中未配置，则发送到全局配置的 `EMAIL_TO` 邮箱

## 配置步骤

### 1. 获取QQ邮箱授权码

QQ邮箱不能直接使用QQ密码登录SMTP服务器，需要使用**授权码**。

#### 步骤：

1. **登录QQ邮箱网页版**
   - 访问：https://mail.qq.com
   - 使用QQ账号和密码登录

2. **开启SMTP服务**
   - 点击右上角"设置" -> "账户"
   - 找到"POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"部分
   - 开启"POP3/SMTP服务"或"IMAP/SMTP服务"
   - 如果之前未开启，系统会要求进行身份验证（手机验证）

3. **生成授权码**
   - 在"POP3/SMTP服务"或"IMAP/SMTP服务"开启后
   - 点击"生成授权码"按钮
   - 按提示发送短信到指定号码
   - 获取16位授权码（例如：`abcdefghijklmnop`）

### 2. 配置后端环境变量

编辑 `backend/.env` 文件，添加以下配置：

```env
# 启用邮件告警功能
EMAIL_ENABLED=true

# QQ邮箱SMTP服务器配置
EMAIL_SMTP_HOST=smtp.qq.com
EMAIL_SMTP_PORT=465

# QQ邮箱账号（完整的QQ邮箱地址）
EMAIL_SMTP_USER=your_qq_email@qq.com

# QQ邮箱授权码（不是QQ密码！）
EMAIL_SMTP_PASSWORD=abcdefghijklmnop

# 发件人邮箱地址（通常与EMAIL_SMTP_USER相同）
EMAIL_FROM=your_qq_email@qq.com

# 默认接收邮箱（可选，多个邮箱用逗号分隔）
# 注意：如果告警规则中配置了email_address，将优先使用规则中的邮箱
EMAIL_TO=recipient1@example.com,recipient2@example.com
```

### 3. 配置告警规则中的接收邮箱（推荐）

在前端"告警规则"页面：

1. 点击"编辑"按钮编辑告警规则
2. 开启"邮件告警"开关
3. 在"接收邮箱"输入框中输入接收告警邮件的邮箱地址
   - 单个邮箱：`user@example.com`
   - 多个邮箱：`user1@example.com,user2@example.com`
4. 点击"保存"

**注意**：告警规则中配置的邮箱优先级高于全局配置的 `EMAIL_TO`。

## QQ邮箱SMTP配置参数

| 配置项 | 值 | 说明 |
|--------|-----|------|
| SMTP服务器 | `smtp.qq.com` | QQ邮箱SMTP服务器地址 |
| SMTP端口 | `465`（推荐）或 `587` | 465使用SSL，587使用STARTTLS |
| 登录账号 | `your_qq_email@qq.com` | 完整的QQ邮箱地址 |
| 登录密码 | 授权码（16位） | **不是QQ密码**，是授权码 |
| 发件人 | `your_qq_email@qq.com` | 通常与登录账号相同 |

## 其他邮箱服务商配置

如果需要使用其他邮箱服务商，可以参考以下配置：

### 163邮箱
```env
EMAIL_SMTP_HOST=smtp.163.com
EMAIL_SMTP_PORT=465
EMAIL_SMTP_USER=your_email@163.com
EMAIL_SMTP_PASSWORD=your_auth_code
EMAIL_FROM=your_email@163.com
```

### Gmail（需要应用专用密码）
```env
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=your_email@gmail.com
EMAIL_SMTP_PASSWORD=your_app_specific_password
EMAIL_FROM=your_email@gmail.com
```

### 企业邮箱（以腾讯企业邮箱为例）
```env
EMAIL_SMTP_HOST=smtp.exmail.qq.com
EMAIL_SMTP_PORT=465
EMAIL_SMTP_USER=your_email@yourcompany.com
EMAIL_SMTP_PASSWORD=your_password
EMAIL_FROM=your_email@yourcompany.com
```

## 测试邮件发送

配置完成后，重启后端服务，系统会在以下情况自动发送邮件：

1. **定时检查触发告警**：当电费余量低于告警阈值时
2. **手动触发告警**：通过API或前端手动触发

## 常见问题

### 1. 提示"535 Login Fail. Please enter your authorization code to login"

**原因**：使用了QQ密码而不是授权码

**解决方法**：
- 确认使用的是授权码，不是QQ密码
- 重新生成授权码并更新配置

### 2. 提示"连接超时"或"无法连接到SMTP服务器"

**原因**：网络问题或端口被防火墙阻止

**解决方法**：
- 检查网络连接
- 尝试使用端口587（STARTTLS）代替465（SSL）
- 检查防火墙设置

### 3. 邮件发送成功但收不到邮件

**原因**：邮件可能被放入垃圾邮件文件夹

**解决方法**：
- 检查垃圾邮件文件夹
- 将发件人邮箱添加到联系人白名单
- 检查接收邮箱的过滤规则

### 4. 提示"发件人地址与登录账号不一致"

**原因**：`EMAIL_FROM` 与 `EMAIL_SMTP_USER` 不一致

**解决方法**：
- 确保 `EMAIL_FROM` 与 `EMAIL_SMTP_USER` 相同（使用QQ邮箱时）

## 安全建议

1. **不要将授权码提交到Git仓库**
   - 确保 `.env` 文件已添加到 `.gitignore`
   - 授权码泄露后应立即重新生成

2. **定期更换授权码**
   - 建议每3-6个月更换一次授权码

3. **使用专用邮箱**
   - 建议使用专门用于系统告警的邮箱账号
   - 避免使用个人重要邮箱

4. **限制接收邮箱**
   - 只配置必要的接收邮箱
   - 避免将告警邮件发送到公开邮箱

## 相关文件

- 配置文件：`backend/.env`
- 配置示例：`backend/.env.example`
- 邮件发送代码：`backend/app/alert.py`
- 邮件模板：`backend/app/templates.py`
