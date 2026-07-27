export interface ApiResult<T> {
  code: number
  message: string
  data: T | null
}

interface ApiRequestOptions {
  url: string
  method?: UniApp.RequestOptions['method']
  data?: UniApp.RequestOptions['data']
}

export const apiBaseUrl = import.meta.env.VITE_API_BASE_URL.replace(/\/$/, '')

export const getAuthorizationHeader = () => {
  const token = uni.getStorageSync<string>('token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export const unwrapApiResult = <T>(result: ApiResult<T>): T => {
  if (result.code !== 200)
    throw new Error(result.message)
  return result.data as T
}

export const apiRequest = <T>(options: ApiRequestOptions): Promise<T> => {
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${apiBaseUrl}/api${options.url}`,
      method: options.method ?? 'GET',
      data: options.data,
      header: getAuthorizationHeader(),
      success: (response) => {
        try {
          resolve(unwrapApiResult(response.data as ApiResult<T>))
        }
        catch (error) {
          reject(error)
        }
      },
      fail: () => reject(new Error('网络请求失败，请稍后重试')),
    })
  })
}

export const getErrorMessage = (error: unknown) => {
  return error instanceof Error ? error.message : '操作失败，请稍后重试'
}
