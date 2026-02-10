-- 添加空调余额和照明余额字段到power_records表
-- 执行方法：mysql -u cxl_database -p dorm_power_guard < add_balance_fields.sql

-- 添加空调余额字段（如果不存在）
ALTER TABLE power_records 
ADD COLUMN IF NOT EXISTS kbalance FLOAT NULL COMMENT '空调余额（元）' AFTER balance;

-- 添加照明余额字段（如果不存在）
ALTER TABLE power_records 
ADD COLUMN IF NOT EXISTS zbalance FLOAT NULL COMMENT '照明余额（元）' AFTER kbalance;

-- 如果MySQL版本不支持IF NOT EXISTS，使用以下方式：
-- ALTER TABLE power_records ADD COLUMN kbalance FLOAT NULL COMMENT '空调余额（元）' AFTER balance;
-- ALTER TABLE power_records ADD COLUMN zbalance FLOAT NULL COMMENT '照明余额（元）' AFTER kbalance;
