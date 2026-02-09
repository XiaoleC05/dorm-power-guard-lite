# 部署文档

## 单机部署方案

本系统设计为可在单台学生服务器上运行，所有组件均可部署在同一台机器上。

## 部署架构

```
┌─────────────────────────────────┐
│     学生服务器（单机）          │
│                                 │
│  ┌──────────┐  ┌──────────┐   │
│  │  Nginx   │  │  MySQL   │   │
│  │ (反向代理)│  │  (数据库) │   │
│  └────┬─────┘  └────┬─────┘   │
│       │             │          │
│  ┌────▼─────────────▼─────┐   │
│  │   FastAPI Backend      │   │
│  │   (端口: 8000)         │   │
│  └────────────────────────┘   │
│                                 │
│  ┌─────────────────────────┐   │
│  │   Vue Frontend          │   │
│  │   (静态文件)             │   │
│  └─────────────────────────┘   │
└─────────────────────────────────┘
```

## 部署步骤

### 1. 系统准备

#### 1.1 安装基础软件

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv nodejs npm mysql-server nginx

# CentOS/RHEL
sudo yum install python3 python3-pip nodejs npm mysql-server nginx
```

#### 1.2 配置MySQL

```bash
# 启动MySQL服务
sudo systemctl start mysql
sudo systemctl enable mysql

# 创建数据库和用户
mysql -u root -p
```

```sql
CREATE DATABASE dorm_power_guard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'dormuser'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON dorm_power_guard.* TO 'dormuser'@'localhost';
FLUSH PRIVILEGES;
```

### 2. 后端部署

#### 2.1 创建Python虚拟环境

```bash
cd /opt/dorm-power-guard-lite/backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 2.2 配置环境变量

```bash
cp .env.example .env
nano .env  # 编辑配置文件
```

#### 2.3 初始化数据库

```bash
python -c "from app.database import init_db; init_db()"
```

#### 2.4 测试运行

```bash
python run.py
```

访问 `http://localhost:8000/docs` 查看API文档。

#### 2.5 使用Supervisor管理进程

安装Supervisor：

```bash
sudo apt install supervisor  # Ubuntu/Debian
sudo yum install supervisor   # CentOS/RHEL
```

创建配置文件 `/etc/supervisor/conf.d/dorm-power-guard.conf`：

```ini
[program:dorm-power-guard]
command=/opt/dorm-power-guard-lite/backend/venv/bin/python /opt/dorm-power-guard-lite/backend/run.py
directory=/opt/dorm-power-guard-lite/backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/dorm-power-guard.log
```

启动服务：

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start dorm-power-guard
```

### 3. 前端部署

#### 3.1 构建前端

```bash
cd /opt/dorm-power-guard-lite/frontend
npm install
npm run build
```

#### 3.2 配置Nginx

创建Nginx配置文件 `/etc/nginx/sites-available/dorm-power-guard`：

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 或使用IP地址

    # 前端静态文件
    location / {
        root /opt/dorm-power-guard-lite/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端API代理
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/dorm-power-guard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 4. 配置QQ机器人（可选）

#### 4.1 使用go-cqhttp

1. 下载go-cqhttp：https://github.com/Mrs4s/go-cqhttp/releases

2. 配置 `config.yml`：

```yaml
account:
  uin: YOUR_QQ_NUMBER
  password: YOUR_QQ_PASSWORD

servers:
  - http:
      host: 0.0.0.0
      port: 5700
```

3. 启动go-cqhttp：

```bash
./go-cqhttp
```

4. 在后端 `.env` 中配置：

```env
QQ_BOT_ENABLED=true
QQ_BOT_TYPE=go-cqhttp
QQ_BOT_API_URL=http://localhost:5700
QQ_BOT_GROUP_ID=123456789
```

### 5. 配置邮件告警（可选）

#### 5.1 QQ邮箱SMTP配置

在 `.env` 中配置：

```env
EMAIL_ENABLED=true
EMAIL_SMTP_HOST=smtp.qq.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=your_email@qq.com
EMAIL_SMTP_PASSWORD=your_auth_code  # QQ邮箱授权码，不是密码
EMAIL_FROM=your_email@qq.com
EMAIL_TO=recipient@example.com
```

**注意**：QQ邮箱需要使用授权码，不是登录密码。获取方式：
1. 登录QQ邮箱
2. 设置 -> 账户 -> 开启SMTP服务
3. 生成授权码

### 6. 防火墙配置

```bash
# 开放HTTP端口
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp  # 如果使用HTTPS

# 如果从外部访问MySQL（不推荐）
# sudo ufw allow 3306/tcp
```

### 7. 定期备份

创建备份脚本 `/opt/dorm-power-guard-lite/backup.sh`：

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/dorm-power-guard"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据库
mysqldump -u dormuser -p'your_password' dorm_power_guard > $BACKUP_DIR/db_$DATE.sql

# 保留最近7天的备份
find $BACKUP_DIR -name "db_*.sql" -mtime +7 -delete
```

设置定时任务：

```bash
chmod +x /opt/dorm-power-guard-lite/backup.sh
crontab -e
```

添加：

```
0 2 * * * /opt/dorm-power-guard-lite/backup.sh
```

## 监控和维护

### 查看日志

```bash
# Supervisor日志
sudo supervisorctl tail -f dorm-power-guard

# Nginx日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# 应用日志（如果配置了文件日志）
tail -f /var/log/dorm-power-guard.log
```

### 重启服务

```bash
# 重启后端
sudo supervisorctl restart dorm-power-guard

# 重启Nginx
sudo systemctl restart nginx

# 重启MySQL
sudo systemctl restart mysql
```

### 更新代码

```bash
cd /opt/dorm-power-guard-lite
git pull

# 更新后端
cd backend
source venv/bin/activate
pip install -r requirements.txt
sudo supervisorctl restart dorm-power-guard

# 更新前端
cd ../frontend
npm install
npm run build
sudo systemctl reload nginx
```

## 故障排查

### 后端无法启动

1. 检查Python环境和依赖：
```bash
source venv/bin/activate
python --version
pip list
```

2. 检查数据库连接：
```bash
mysql -u dormuser -p -h localhost dorm_power_guard
```

3. 检查端口占用：
```bash
netstat -tlnp | grep 8000
```

### 前端无法访问

1. 检查Nginx配置：
```bash
sudo nginx -t
```

2. 检查静态文件路径：
```bash
ls -la /opt/dorm-power-guard-lite/frontend/dist
```

3. 检查Nginx日志：
```bash
sudo tail -f /var/log/nginx/error.log
```

### 爬虫不工作

1. 检查爬虫配置：
```bash
cat backend/.env | grep CRAWLER
```

2. 手动测试爬虫：
```bash
cd backend
source venv/bin/activate
python -c "from app.crawler import get_crawler; c = get_crawler(); print(c.test_connection())"
```

3. 检查定时任务：
```bash
# 查看Supervisor日志中的定时任务启动信息
sudo supervisorctl tail dorm-power-guard | grep scheduler
```

## 性能优化建议

1. **数据库优化**：
   - 定期清理旧数据（保留最近3个月）
   - 添加适当的索引
   - 配置MySQL连接池

2. **爬虫优化**：
   - 合理设置请求间隔，避免被封IP
   - 使用Session复用连接
   - 添加重试机制

3. **前端优化**：
   - 启用Nginx gzip压缩
   - 配置浏览器缓存
   - 使用CDN加速（可选）

## 安全建议

1. **生产环境配置**：
   - 修改默认数据库密码
   - 限制MySQL只允许本地连接
   - 配置HTTPS（使用Let's Encrypt免费证书）
   - 修改CORS配置，限制前端访问来源

2. **访问控制**：
   - 考虑添加API认证（JWT Token）
   - 限制管理接口的访问IP

3. **数据安全**：
   - 定期备份数据库
   - 加密敏感配置信息
   - 不要在代码中硬编码密码
