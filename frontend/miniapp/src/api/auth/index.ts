import type { WechatLoginResponse } from './type'
import type { ApiResult } from '@/utils/api'
import { apiBaseUrl, unwrapApiResult } from '@/utils/api'

export const authApi = {
  wechatLogin(code: string): Promise<WechatLoginResponse> {
    return new Promise((resolve, reject) => {
      uni.request({
        url: `${apiBaseUrl}/api/auth/wechat-login`,
        method: 'POST',
        data: { code },
        success: (response) => {
          try {
            resolve(unwrapApiResult(response.data as ApiResult<WechatLoginResponse>))
          }
          catch (error) {
            reject(error)
          }
        },
        fail: () => reject(new Error('登录请求失败，请稍后重试')),
      })
    })
  },
}
