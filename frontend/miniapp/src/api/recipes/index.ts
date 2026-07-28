import type { RecipeDetail, RecipeListParams, RecipePage, RecipePayload, RecipeSavedResult, RecipeShareDetail } from './type'
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
  share(recipeId: string) {
    return apiRequest<void>({ url: `/recipes/${recipeId}/share`, method: 'POST' })
  },
  sharedDetail(recipeId: string) {
    return apiRequest<RecipeShareDetail>({ url: `/recipes/shares/${recipeId}` })
  },
  saveShared(recipeId: string) {
    return apiRequest<RecipeSavedResult>({ url: `/recipes/shares/${recipeId}/save`, method: 'POST' })
  },
}
