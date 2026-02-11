import api from './index'

// 手动触发爬虫
export const manualCrawl = () => api.post('/system/crawl')

// 获取QQ机器人全局配置
export const getQQConfig = () => api.get('/system/qq-config')
