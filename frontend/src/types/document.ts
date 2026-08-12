export interface CreateDocumentRequest {
  document_name: string
  document_type: string
}

export interface DocumentItem {
  id: string
  document_name: string
  document_type: string
}

export interface DocumentSearchResult {
  id: string
  document_name: string
  document_type: string
  is_signed: boolean
  signed_by?: string
  uploaded_by: string
  uploaded_at: string
  file_url: string
}

export interface SignDocumentResponse {
  document_id: string
  signed: boolean
  signature_id: string
}

export interface DocumentVerification {
  document_name: string
  document_type: string
  is_signed: boolean
  uploaded_at: string
  verified: boolean
}
