import api from './index'

export const getCurrentAlertRule = () => api.get('/alert/rules')

export const createAlertRule = (data) => api.post('/alert/rules', data)

export const updateCurrentAlertRule = (data) => api.put('/alert/rules', data)

export const getAlertLogs = (dormNumber = null, limit = 50) =>
  api.get('/alert/logs', { params: { dorm_number: dormNumber, limit } })
