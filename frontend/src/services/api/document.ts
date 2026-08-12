import { apiClient } from "./client"
import type {
  CreateDocumentRequest,
  DocumentItem,
  DocumentVerification,
  DocumentSearchResult,
  SignDocumentResponse,
} from "@/types/document"

export const documentApi = {
  uploadDocument: async (data: CreateDocumentRequest & { file: File }): Promise<{ id: string; qr_code: string; file_url: string }> => {
    const formData = new FormData()
    formData.append("document_name", data.document_name)
    formData.append("document_type", data.document_type)
    formData.append("file", data.file)

    const res = await apiClient.post("/documents/upload", formData)
    return res.data
  },

  verifyDocument: async (documentId: string): Promise<DocumentVerification> => {
    const res = await apiClient.get(`/documents/verify/${documentId}`)
    return res.data
  },

  getMyDocuments: async (): Promise<DocumentItem[]> => {
    const res = await apiClient.get("/documents/my-documents")
    return res.data
  },

  searchDocuments: async (params: {
    document_type?: string
    uploaded_by?: string
    signed?: boolean
  }): Promise<DocumentSearchResult[]> => {
    const res = await apiClient.get("/documents/search", { params })
    return res.data
  },

  signDocument: async (documentId: string): Promise<SignDocumentResponse> => {
    const res = await apiClient.post(`/documents/${documentId}/sign`)
    return res.data
  },
}
