import api from './index'

// 创建告警规则
export const createAlertRule = (data) => api.post('/alert/rules', data)

// 获取当前告警规则（单一宿舍）
export const getCurrentAlertRule = () => api.get('/alert/rules')

// 获取所有告警规则（兼容接口）
export const getAllAlertRules = () => api.get('/alert/rules')

// 获取告警规则（兼容接口）
export const getAlertRule = (dormNumber) => api.get(`/alert/rules/${dormNumber}`)

// 更新当前告警规则（单一宿舍）
export const updateCurrentAlertRule = (data) => api.put('/alert/rules', data)

// 更新告警规则（兼容接口）
export const updateAlertRule = (dormNumber, data) => 
  api.put(`/alert/rules/${dormNumber}`, data)

// 删除当前告警规则（单一宿舍）
export const deleteCurrentAlertRule = () => api.delete('/alert/rules')

// 删除告警规则（兼容接口）
export const deleteAlertRule = (dormNumber) => api.delete(`/alert/rules/${dormNumber}`)

// 获取告警日志
export const getAlertLogs = (dormNumber = null, limit = 50) =>
  api.get('/alert/logs', { params: { dorm_number: dormNumber, limit } })
