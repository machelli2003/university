import { apiClient } from "./client"
import type { LibraryBook, BorrowBookRequest, Borrowing } from "@/types/library"

export const libraryApi = {
  searchBooks: async (query: string): Promise<LibraryBook[]> => {
    const res = await apiClient.get("/library/books/search", { params: { query } })
    return res.data
  },

  createBook: async (data: { title: string; isbn?: string; author: string; publisher?: string; category: string; total_copies: number }) => {
    const res = await apiClient.post('/library/books', data)
    return res.data
  },

  borrowBook: async (data: BorrowBookRequest) => {
    const res = await apiClient.post("/library/borrow", data)
    return res.data
  },

  returnBook: async (borrowingId: string) => {
    const res = await apiClient.post("/library/return", { borrowing_id: borrowingId })
    return res.data
  },

  getMyBorrowings: async (studentId: string): Promise<Borrowing[]> => {
    const res = await apiClient.get(`/library/my-borrowings/${studentId}`)
    return res.data
  },
}
