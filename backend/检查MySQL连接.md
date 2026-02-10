# MySQL 连接检查指南

## 当前状态

- ✅ MySQL 服务正在运行（端口 3306 已开放）
- ❌ 使用密码 `783688` 无法连接 root 用户

## 请确认以下信息

### 1. 确认 root 密码

请尝试手动登录 MySQL 确认密码：

```powershell
mysql -u root -p
```

输入密码 `783688`，如果能够登录，说明密码正确。

### 2. 如果密码不是 783688

请告诉我正确的 root 密码，我会更新配置文件。

### 3. 如果忘记 root 密码

可以重置 root 密码，或者创建一个新用户：

```sql
-- 创建新用户（使用 root 登录后执行）
CREATE USER 'dormuser'@'localhost' IDENTIFIED BY '783688';
GRANT ALL PRIVILEGES ON dorm_power_guard.* TO 'dormuser'@'localhost';
FLUSH PRIVILEGES;
```

然后在 `.env` 文件中使用：
```env
DB_USER=dormuser
DB_PASSWORD=783688
```

## 快速测试

运行以下命令测试连接：

```powershell
cd c:\GitCloneRepository\dorm-power-guard-lite\backend
python test_db_connection.py
```

## 下一步

确认密码后，我会：
1. 更新 `.env` 文件中的密码
2. 测试数据库连接
3. 启动后端服务
