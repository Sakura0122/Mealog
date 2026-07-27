import type { UploadFileResponse } from './type'
import type { ApiResult } from '@/utils/request'
import { apiBaseUrl, getAuthorizationHeader, unwrapApiResult } from '@/utils/request'

type ImageUploadType = 'avatar' | 'images'

const uploadImage = (
  filePath: string,
  uploadType: ImageUploadType,
  failureMessage: string,
): Promise<UploadFileResponse> => {
  return new Promise((resolve, reject) => {
    uni.uploadFile({
      url: `${apiBaseUrl}/api/files/upload`,
      filePath,
      name: 'file',
      formData: { type: uploadType },
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
      fail: () => reject(new Error(failureMessage)),
    })
  })
}

export const fileApi = {
  uploadImage(filePath: string): Promise<UploadFileResponse> {
    return uploadImage(filePath, 'images', '封面上传失败，请稍后重试')
  },
  uploadAvatar(filePath: string): Promise<UploadFileResponse> {
    return uploadImage(filePath, 'avatar', '头像上传失败，请稍后重试')
  },
}
