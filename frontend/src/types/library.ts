export interface LibraryBook {
  id: string
  title: string
  author: string
  available_copies: number
  total_copies: number
}

export interface BorrowBookRequest {
  student_id: string
  book_id: string
  days?: number
}

export interface Borrowing {
  id: string
  book_id: string
  due_date: string
}
