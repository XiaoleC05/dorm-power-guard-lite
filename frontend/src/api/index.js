import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    // 204 No Content响应，返回null
    if (response.status === 204) {
      return null
    }
    return response.data
  },
  error => {
    // 404或204错误（未找到记录）静默处理，不输出错误日志
    // 这是正常情况，因为某些宿舍可能还没有数据或规则
    if (error.response?.status === 404 || error.response?.status === 204) {
      // 静默处理404/204，直接reject让调用方处理，不输出任何日志
      return Promise.reject(error)
    }
    // 网络错误或其他错误才输出日志
    if (!error.response) {
      // 网络错误（如连接失败）
      console.error('Network Error:', error.message)
    } else {
      // 其他HTTP错误（500等）
      const message = error.response?.data?.detail || error.message || '请求失败'
      // 500错误才输出日志，其他错误静默处理
      if (error.response?.status === 500) {
        console.error('API Error:', message)
      }
    }
    return Promise.reject(error)
  }
)

export default api
