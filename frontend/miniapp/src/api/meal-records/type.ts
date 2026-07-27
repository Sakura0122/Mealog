export type MealSourceType = 'SELF_MADE' | 'DINING_OUT'
export type RecipeStatus = 'DRAFT' | 'COMPLETED'

export interface MealRecordImageInput {
  original_object_key: string
  processed_object_key: string | null
}

export interface MealRecordPayload {
  dish_name: string
  eaten_at: string
  source_type: MealSourceType | null
  store_id: string | null
  recipe_id: string | null
  note: string | null
  images: MealRecordImageInput[]
}

export interface MealRecordListItem {
  id: string
  dish_name: string
  eaten_at: string
  note: string | null
  cover_url: string | null
}

export interface MealRecordPage {
  total: number
  page_count: number
  list: MealRecordListItem[]
}

export interface MealRecordListParams {
  current_page: number
  page_size: number
  date?: string
}

export interface MealRecordCalendarDay {
  date: string
  record_count: number
  cover_url: string | null
}

export interface MealRecordCalendar {
  month: string
  total: number
  recorded_days: number
  days: MealRecordCalendarDay[]
}

export interface MealRecordImage extends MealRecordImageInput {
  id: string
  original_url: string
  processed_url: string | null
  sort_order: number
  is_cover: boolean
}

export interface MealRecordDetail extends Omit<MealRecordPayload, 'images'> {
  id: string
  store_name: string | null
  store_address: string | null
  recipe_name: string | null
  recipe_status: RecipeStatus | null
  images: MealRecordImage[]
  created_at: string
  updated_at: string
}
