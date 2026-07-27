import type { UserProfile, UserProfilePayload, UserStatistics } from './type'
import { apiRequest } from '@/utils/request'

export const userApi = {
  profile() {
    return apiRequest<UserProfile>({ url: '/users/me' })
  },
  updateProfile(payload: UserProfilePayload) {
    return apiRequest<UserProfile>({ url: '/users/me', method: 'PUT', data: payload })
  },
  statistics() {
    return apiRequest<UserStatistics>({ url: '/users/me/statistics' })
  },
}
