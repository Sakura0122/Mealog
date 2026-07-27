export interface WechatLoginUser {
  id: string
  nickname: string | null
  avatar_object_key: string | null
}

export interface WechatLoginResponse {
  token: string
  user: WechatLoginUser
}
