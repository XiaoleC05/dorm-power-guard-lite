import api from './index'

// 手动触发爬虫
export const manualCrawl = () => api.post('/system/crawl')
