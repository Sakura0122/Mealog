import type { RecipeDetail, RecipeListParams, RecipePage, RecipePayload } from './type'
import { apiRequest } from '@/utils/request'

export const recipeApi = {
  list(params: RecipeListParams) {
    return apiRequest<RecipePage>({ url: '/recipes', data: params })
  },
  detail(recipeId: string) {
    return apiRequest<RecipeDetail>({ url: `/recipes/${recipeId}` })
  },
  create(payload: RecipePayload) {
    return apiRequest<void>({ url: '/recipes', method: 'POST', data: payload })
  },
  update(recipeId: string, payload: RecipePayload) {
    return apiRequest<void>({ url: `/recipes/${recipeId}`, method: 'PUT', data: payload })
  },
  remove(recipeId: string) {
    return apiRequest<void>({ url: `/recipes/${recipeId}`, method: 'DELETE' })
  },
}
