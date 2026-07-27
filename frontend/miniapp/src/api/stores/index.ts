import type { StoreItem, StoreListParams, StorePage, StorePayload } from './type'
import { apiRequest } from '@/utils/request'

export const storeApi = {
  list(params: StoreListParams) {
    return apiRequest<StorePage>({ url: '/stores', data: params })
  },
  create(payload: StorePayload) {
    return apiRequest<StoreItem>({ url: '/stores', method: 'POST', data: payload })
  },
}
