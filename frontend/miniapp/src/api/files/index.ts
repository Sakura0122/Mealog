import type { UploadFileResponse } from './type'
import type { ApiResult } from '@/utils/request'
import { apiBaseUrl, getAuthorizationHeader, unwrapApiResult } from '@/utils/request'

export const fileApi = {
  uploadImage(filePath: string): Promise<UploadFileResponse> {
    return new Promise((resolve, reject) => {
      uni.uploadFile({
        url: `${apiBaseUrl}/api/files/upload`,
        filePath,
        name: 'file',
        formData: { type: 'images' },
        header: getAuthorizationHeader(),
        success: (response) => {
          try {
            const result = JSON.parse(response.data) as ApiResult<UploadFileResponse>
            resolve(unwrapApiResult(result))
          }
          catch (error) {
            reject(error)
          }
        },
        fail: () => reject(new Error('封面上传失败，请稍后重试')),
      })
    })
  },
}
