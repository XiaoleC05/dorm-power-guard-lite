/** 将 axios / FastAPI 错误转为可读字符串 */
export function formatApiError(error, fallback = '操作失败') {
  const detail = error?.response?.data?.detail
  if (!detail) {
    return error?.response?.data?.message || error?.message || fallback
  }
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg || `${item.loc?.join('.')}: ${item.msg}`).join('；')
  }
  return fallback
}
