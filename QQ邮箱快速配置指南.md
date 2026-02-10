# QQ邮箱快速配置指南

## 快速开始

### 1. 获取QQ邮箱授权码

1. 登录QQ邮箱：https://mail.qq.com
2. 设置 → 账户 → 开启"POP3/SMTP服务"
3. 点击"生成授权码"，按提示获取16位授权码

### 2. 配置 `.env` 文件

编辑 `backend/.env` 文件，修改以下配置：

```env
# 启用邮件告警
EMAIL_ENABLED=true

# QQ邮箱SMTP配置
EMAIL_SMTP_HOST=smtp.qq.com
EMAIL_SMTP_PORT=465
EMAIL_SMTP_USER=你的QQ邮箱@qq.com
EMAIL_SMTP_PASSWORD=你的16位授权码
EMAIL_FROM=你的QQ邮箱@qq.com

# 默认接收邮箱（可选，告警规则中的邮箱优先级更高）
EMAIL_TO=接收邮箱1@example.com,接收邮箱2@example.com
```

### 3. 重启后端服务

配置完成后，重启后端服务使配置生效。

### 4. 配置告警规则接收邮箱（推荐）

在前端页面：
1. 进入"告警规则"页面
2. 点击"编辑"
3. 开启"邮件告警"
4. 在"接收邮箱"输入框中输入接收邮箱（多个用逗号分隔）
5. 保存

## 配置示例

假设你的QQ邮箱是 `123456789@qq.com`，授权码是 `abcdefghijklmnop`，要发送到 `user@example.com`：

```env
EMAIL_ENABLED=true
EMAIL_SMTP_HOST=smtp.qq.com
EMAIL_SMTP_PORT=465
EMAIL_SMTP_USER=123456789@qq.com
EMAIL_SMTP_PASSWORD=abcdefghijklmnop
EMAIL_FROM=123456789@qq.com
EMAIL_TO=user@example.com
```

## 注意事项

1. **授权码不是QQ密码**：必须使用授权码，不能使用QQ密码
2. **端口选择**：推荐使用465（SSL），如果不行可以尝试587（STARTTLS）
3. **优先级**：告警规则中配置的邮箱优先级高于 `EMAIL_TO`
4. **多个邮箱**：用逗号分隔，例如：`user1@qq.com,user2@qq.com`

## 测试

配置完成后，当电费余量低于告警阈值时，系统会自动发送邮件到配置的邮箱。
