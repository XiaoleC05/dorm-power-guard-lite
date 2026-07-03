import api from './index'

// 手动触发爬虫
export const manualCrawl = () => api.post('/system/crawl')

// 获取QQ机器人全局配置
export const getQQConfig = () => api.get('/system/qq-config')

// 获取系统配置信息
export const getConfig = () => api.get('/system/config')

// 检查QQ机器人连接状态
export const checkQQStatus = () => api.get('/system/qq-status')

// 发送 QQ 实时电费报告
export const sendPowerReport = () => api.post('/system/report')
