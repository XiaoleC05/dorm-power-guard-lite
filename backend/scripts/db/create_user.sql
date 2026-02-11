-- 创建数据库用户并授权的SQL脚本
-- 使用方法：mysql -u root -p < create_user.sql
-- 或者登录MySQL后执行以下命令

-- 创建用户
-- 注意：如果用户已存在，此命令会报错，可以忽略
CREATE USER 'cxldatabase'@'localhost' IDENTIFIED BY '783688';

-- 授予权限
GRANT ALL PRIVILEGES ON dorm_power_guard.* TO 'cxldatabase'@'localhost';

-- 刷新权限
FLUSH PRIVILEGES;

-- 验证用户创建
SELECT User, Host FROM mysql.user WHERE User='cxldatabase';
