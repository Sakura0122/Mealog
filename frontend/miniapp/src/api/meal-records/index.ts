import type {
  MealRecordCalendar,
  MealRecordDetail,
  MealRecordListParams,
  MealRecordPage,
  MealRecordPayload,
} from './type'
import { apiRequest } from '@/utils/request'

export const mealRecordApi = {
  list(params: MealRecordListParams) {
    return apiRequest<MealRecordPage>({ url: '/meal-records', data: params })
  },
  calendar(month: string) {
    return apiRequest<MealRecordCalendar>({ url: '/meal-records/calendar', data: { month } })
  },
  detail(recordId: string) {
    return apiRequest<MealRecordDetail>({ url: `/meal-records/${recordId}` })
  },
  create(payload: MealRecordPayload) {
    return apiRequest<void>({ url: '/meal-records', method: 'POST', data: payload })
  },
  update(recordId: string, payload: MealRecordPayload) {
    return apiRequest<void>({ url: `/meal-records/${recordId}`, method: 'PUT', data: payload })
  },
  remove(recordId: string) {
    return apiRequest<void>({ url: `/meal-records/${recordId}`, method: 'DELETE' })
  },
}
