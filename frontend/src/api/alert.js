import api from './index'

// 创建告警规则
export const createAlertRule = (data) => api.post('/alert/rules', data)

// 获取所有告警规则
export const getAllAlertRules = () => api.get('/alert/rules')

// 获取告警规则
export const getAlertRule = (dormNumber) => api.get(`/alert/rules/${dormNumber}`)

// 更新告警规则
export const updateAlertRule = (dormNumber, data) => 
  api.put(`/alert/rules/${dormNumber}`, data)

// 删除告警规则
export const deleteAlertRule = (dormNumber) => api.delete(`/alert/rules/${dormNumber}`)

// 获取告警日志
export const getAlertLogs = (dormNumber = null, limit = 50) =>
  api.get('/alert/logs', { params: { dorm_number: dormNumber, limit } })
