export type RecipeStatus = 'DRAFT' | 'COMPLETED'

export interface RecipePayload {
  name: string
  cover_object_key: string | null
  ingredients: string[]
  steps: string | null
}

export interface RecipeListItem {
  id: string
  name: string
  cover_url: string | null
  status: RecipeStatus
  usage_count: number
  updated_at: string
}

export interface RecipeDetail extends RecipePayload {
  id: string
  cover_url: string | null
  status: RecipeStatus
  usage_count: number
  created_at: string
  updated_at: string
}

export interface RecipePage {
  total: number
  page_count: number
  list: RecipeListItem[]
}

export interface RecipeListParams {
  current_page: number
  page_size: number
  keyword?: string
  status?: RecipeStatus
}
