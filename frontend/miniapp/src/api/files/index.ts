import type { UploadFileResponse } from './type'
import type { ApiResult } from '@/utils/api'
import { apiBaseUrl, unwrapApiResult } from '@/utils/api'
import { getAuthorizationHeader, withAuthRetry } from '@/utils/request'

type ImageUploadType = 'avatar' | 'images'

const compressImage = async (filePath: string): Promise<string> => {
  try {
    const imageInfo = await uni.getImageInfo({ src: filePath })
    // 微信 iOS 仅支持压缩 JPEG，其他格式交由后端统一转码压缩。
    if (!imageInfo.type || !['jpg', 'jpeg'].includes(imageInfo.type.toLowerCase()))
      return filePath

    const result = await uni.compressImage({ src: filePath, quality: 80 })
    return result.tempFilePath
  }
  catch {
    throw new Error('图片压缩失败，请重新选择图片')
  }
}

const uploadImage = async (
  filePath: string,
  uploadType: ImageUploadType,
  failureMessage: string,
): Promise<UploadFileResponse> => {
  const compressedFilePath = await compressImage(filePath)
  return withAuthRetry(() => {
    return new Promise((resolve, reject) => {
      uni.uploadFile({
        url: `${apiBaseUrl}/api/files/upload`,
        filePath: compressedFilePath,
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
  })
}

export const fileApi = {
  uploadImage(filePath: string): Promise<UploadFileResponse> {
    return uploadImage(filePath, 'images', '图片上传失败，请稍后重试')
  },
  uploadAvatar(filePath: string): Promise<UploadFileResponse> {
    return uploadImage(filePath, 'avatar', '头像上传失败，请稍后重试')
  },
}
