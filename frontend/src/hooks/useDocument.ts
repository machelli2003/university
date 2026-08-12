import { useMutation, useQuery } from "@tanstack/react-query"
import { documentApi } from "@/services/api/document"
import type { CreateDocumentRequest } from "@/types/document"

export function useUploadDocument() {
  return useMutation({
    mutationFn: (data: CreateDocumentRequest & { file: File }) => documentApi.uploadDocument(data),
  })
}

export function useMyDocuments() {
  return useQuery({
    queryKey: ["my-documents"],
    queryFn: () => documentApi.getMyDocuments(),
  })
}

export function useVerifyDocument(documentId: string | null) {
  return useQuery({
    queryKey: ["document-verify", documentId],
    queryFn: () => documentApi.verifyDocument(documentId!),
    enabled: !!documentId,
  })
}

export function useSearchDocuments(params: { document_type?: string; uploaded_by?: string; signed?: boolean }) {
  return useQuery({
    queryKey: ["documents-search", params],
    queryFn: () => documentApi.searchDocuments(params),
    enabled: !!params.document_type || !!params.uploaded_by || params.signed !== undefined,
  })
}

export function useSignDocument() {
  return useMutation({
    mutationFn: (documentId: string) => documentApi.signDocument(documentId),
  })
}
