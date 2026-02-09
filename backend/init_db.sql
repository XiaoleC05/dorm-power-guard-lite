-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS dorm_power_guard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE dorm_power_guard;

-- 注意：表结构会由SQLAlchemy自动创建，此文件仅供参考
-- 如果需要手动创建，可以使用以下SQL

-- 电费记录表
CREATE TABLE IF NOT EXISTS power_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dorm_number VARCHAR(50) NOT NULL COMMENT '宿舍号',
    balance FLOAT NOT NULL COMMENT '电费余额',
    power_consumption FLOAT COMMENT '用电量（度）',
    record_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录时间',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_dorm_number (dorm_number),
    INDEX idx_record_time (record_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='电费记录表';

-- 告警规则表
CREATE TABLE IF NOT EXISTS alert_rules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dorm_number VARCHAR(50) NOT NULL COMMENT '宿舍号',
    threshold FLOAT NOT NULL COMMENT '告警阈值（元）',
    enabled BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否启用',
    email_enabled BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否启用邮件告警',
    qq_enabled BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否启用QQ告警',
    last_alert_time DATETIME COMMENT '最后告警时间',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_dorm_number (dorm_number),
    INDEX idx_enabled (enabled)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='告警规则表';

-- 告警日志表
CREATE TABLE IF NOT EXISTS alert_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dorm_number VARCHAR(50) NOT NULL COMMENT '宿舍号',
    balance FLOAT NOT NULL COMMENT '触发告警时的余额',
    threshold FLOAT NOT NULL COMMENT '告警阈值',
    alert_type VARCHAR(20) NOT NULL COMMENT '告警类型：email/qq',
    alert_status VARCHAR(20) NOT NULL COMMENT '告警状态：success/failed',
    alert_message TEXT COMMENT '告警消息',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_dorm_number (dorm_number),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='告警日志表';
