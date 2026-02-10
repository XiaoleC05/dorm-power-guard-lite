-- 添加用电量字段和告警阈值字段的迁移脚本

-- 1. 为 power_records 表添加空调用电量和照明用电量字段
ALTER TABLE power_records 
ADD COLUMN kpower_consumption FLOAT NULL COMMENT '空调用电量（度，与上次记录的差值）' AFTER zbalance,
ADD COLUMN zpower_consumption FLOAT NULL COMMENT '照明用电量（度，与上次记录的差值）' AFTER kpower_consumption;

-- 2. 修改 power_records 表的注释
ALTER TABLE power_records 
MODIFY COLUMN kbalance FLOAT NULL COMMENT '空调余量（度）',
MODIFY COLUMN zbalance FLOAT NULL COMMENT '照明余量（度）',
MODIFY COLUMN balance FLOAT NOT NULL COMMENT '电费余量（度，主要监控项，通常是空调余量）',
MODIFY COLUMN power_consumption FLOAT NULL COMMENT '用电量（度，已废弃，使用kpower_consumption和zpower_consumption）';

-- 3. 为 alert_rules 表添加空调阈值和照明阈值字段
ALTER TABLE alert_rules 
ADD COLUMN kthreshold FLOAT NULL COMMENT '空调告警阈值（度）' AFTER dorm_number,
ADD COLUMN zthreshold FLOAT NULL COMMENT '照明告警阈值（度）' AFTER kthreshold;

-- 4. 将旧的 threshold 值迁移到 kthreshold（如果存在）
UPDATE alert_rules SET kthreshold = threshold WHERE kthreshold IS NULL AND threshold IS NOT NULL;

-- 5. 修改 threshold 字段为可空（保留兼容性）
ALTER TABLE alert_rules 
MODIFY COLUMN threshold FLOAT NULL COMMENT '告警阈值（度，已废弃，使用kthreshold和zthreshold）';

-- 6. 为 alert_logs 表添加告警类型字段
ALTER TABLE alert_logs 
ADD COLUMN alert_category VARCHAR(20) NULL COMMENT '告警类别：ac（空调）/light（照明）' AFTER dorm_number,
MODIFY COLUMN balance FLOAT NOT NULL COMMENT '触发告警时的余量（度）',
MODIFY COLUMN threshold FLOAT NOT NULL COMMENT '告警阈值（度）';
