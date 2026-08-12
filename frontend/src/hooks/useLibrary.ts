import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { libraryApi } from "@/services/api/library"
import type { BorrowBookRequest } from "@/types/library"

export function useSearchBooks(query: string) {
  return useQuery({
    queryKey: ["library-books", query],
    queryFn: () => libraryApi.searchBooks(query),
    enabled: query.length > 1,
  })
}

export function useBorrowBook() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: BorrowBookRequest) => libraryApi.borrowBook(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["my-borrowings"] }),
  })
}

export function useMyBorrowings(studentId: string | null) {
  return useQuery({
    queryKey: ["my-borrowings", studentId],
    queryFn: () => libraryApi.getMyBorrowings(studentId!),
    enabled: !!studentId,
  })
}

export function useReturnBook() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (borrowingId: string) => libraryApi.returnBook(borrowingId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["my-borrowings"] }),
  })
}

export function useCreateBook() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: any) => libraryApi.createBook(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["library-books"] }),
  })
}
