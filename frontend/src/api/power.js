import api from './index'

// 创建电费记录
export const createRecord = (data) => api.post('/power/records', data)

// 获取最新记录
export const getLatestRecord = (dormNumber) => api.get(`/power/records/${dormNumber}/latest`)

// 获取记录列表
export const getRecords = (dormNumber, limit = 100) => 
  api.get(`/power/records/${dormNumber}`, { params: { limit } })

// 按日期范围获取记录
export const getRecordsByRange = (dormNumber, startDate, endDate) =>
  api.get(`/power/records/${dormNumber}/range`, {
    params: { start_date: startDate, end_date: endDate }
  })
