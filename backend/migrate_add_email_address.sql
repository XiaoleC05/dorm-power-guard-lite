-- 添加邮箱地址字段的迁移脚本

-- 为 alert_rules 表添加邮箱地址字段
ALTER TABLE alert_rules 
ADD COLUMN email_address VARCHAR(255) NULL COMMENT '邮件告警接收邮箱地址' AFTER email_enabled;
