export interface UploadFileResponse {
  object_key: string
  url: string
  processed_object_key: string | null
  processed_url: string | null
}
