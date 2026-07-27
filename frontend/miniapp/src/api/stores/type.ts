export interface StorePayload {
  name: string
  address: string | null
  latitude: number
  longitude: number
}

export interface StoreItem {
  id: string
  name: string
  address: string | null
  latitude: number | null
  longitude: number | null
  usage_count: number
  updated_at: string
}

export interface StorePage {
  total: number
  page_count: number
  list: StoreItem[]
}

export interface StoreListParams {
  current_page: number
  page_size: number
  keyword?: string
}
