export interface ApiResult<T> {
  code: number
  message: string
  data: T | null
}

export class ApiError extends Error {
  constructor(
    public readonly code: number,
    message: string,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

const configuredApiBaseUrl = import.meta.env.VITE_API_BASE_URL
if (!configuredApiBaseUrl)
  throw new Error('缺少 VITE_API_BASE_URL 配置')

export const apiBaseUrl = configuredApiBaseUrl.replace(/\/$/, '')

export const unwrapApiResult = <T>(result: ApiResult<T>): T => {
  if (result.code !== 200)
    throw new ApiError(result.code, result.message)
  return result.data as T
}
