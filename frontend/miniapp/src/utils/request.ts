import type { ApiResult } from './api'
import { authApi } from '@/api/auth'
import { apiBaseUrl, ApiError, unwrapApiResult } from './api'

interface ApiRequestOptions {
  url: string
  method?: UniApp.RequestOptions['method']
  data?: UniApp.RequestOptions['data']
}

const TOKEN_STORAGE_KEY = 'token'
let authInitialized = false
let loginPromise: Promise<void> | null = null

export const getAuthorizationHeader = () => {
  const token = uni.getStorageSync<string>(TOKEN_STORAGE_KEY)
  return token ? { Authorization: `Bearer ${token}` } : {}
}

const getWechatLoginCode = (): Promise<string> => {
  return new Promise((resolve, reject) => {
    uni.login({
      success: ({ code }) => code
        ? resolve(code)
        : reject(new Error('微信登录未返回有效凭证')),
      fail: () => reject(new Error('微信登录失败，请稍后重试')),
    })
  })
}

const login = (): Promise<void> => {
  if (loginPromise)
    return loginPromise

  loginPromise = (async () => {
    const code = await getWechatLoginCode()
    const result = await authApi.wechatLogin(code)
    uni.setStorageSync(TOKEN_STORAGE_KEY, result.token)
    authInitialized = true
  })()
    .catch((error) => {
      authInitialized = false
      uni.removeStorageSync(TOKEN_STORAGE_KEY)
      throw error
    })
    .finally(() => {
      loginPromise = null
    })

  return loginPromise
}

// 应用启动和首个业务请求共用同一次登录，确保业务接口不会早于 token 获取完成。
export const initializeAuth = (): Promise<void> => login()

const ensureAuth = async () => {
  if (loginPromise) {
    await loginPromise
    return
  }
  if (!authInitialized || !uni.getStorageSync<string>(TOKEN_STORAGE_KEY))
    await login()
}

const refreshAuth = async (expiredToken: string) => {
  const currentToken = uni.getStorageSync<string>(TOKEN_STORAGE_KEY)
  // 其他请求已完成重登时直接复用新 token，避免同一批 401 串行触发多次登录。
  if (currentToken && currentToken !== expiredToken)
    return

  authInitialized = false
  uni.removeStorageSync(TOKEN_STORAGE_KEY)
  await login()
}

export const withAuthRetry = async <T>(request: () => Promise<T>): Promise<T> => {
  await ensureAuth()
  const requestToken = uni.getStorageSync<string>(TOKEN_STORAGE_KEY)

  try {
    return await request()
  }
  catch (error) {
    if (!(error instanceof ApiError) || error.code !== 401)
      throw error

    await refreshAuth(requestToken)
    // 过期请求只重放一次；重放仍未授权时直接抛出，防止形成登录循环。
    return request()
  }
}

const omitUndefinedFields = (data: ApiRequestOptions['data']) => {
  if (data === null || typeof data !== 'object' || Array.isArray(data) || data instanceof ArrayBuffer)
    return data

  // 小程序会把查询对象中的 undefined 序列化为字符串，发送前按可选字段语义将其移除。
  return Object.fromEntries(Object.entries(data).filter(([, value]) => value !== undefined))
}

const requestOnce = <T>(options: ApiRequestOptions): Promise<T> => {
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${apiBaseUrl}/api${options.url}`,
      method: options.method ?? 'GET',
      data: omitUndefinedFields(options.data),
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

export const apiRequest = <T>(options: ApiRequestOptions): Promise<T> => {
  // options 保留了失败请求的完整参数，重登后可以原样重放。
  return withAuthRetry(() => requestOnce<T>(options))
}

export const getErrorMessage = (error: unknown) => {
  return error instanceof Error ? error.message : '操作失败，请稍后重试'
}
