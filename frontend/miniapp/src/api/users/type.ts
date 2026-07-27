export interface UserProfile {
  id: string
  nickname: string | null
  avatar_object_key: string | null
  avatar_url: string | null
}

export interface UserProfilePayload {
  nickname: string
  avatar_object_key: string | null
}

export interface UserStatistics {
  total_records: number
  recorded_days: number
}
