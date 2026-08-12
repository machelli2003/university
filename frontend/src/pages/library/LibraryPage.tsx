import { useState } from "react"
import { AppShell } from "@/components/layout/AppShell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { ErrorAlert, SuccessAlert, Spinner } from "@/components/ui/Feedback"
import { useAuthStore } from "@/store/authStore"
import { useSearchBooks, useBorrowBook, useMyBorrowings, useReturnBook } from "@/hooks/useLibrary"
import { getErrorMessage } from "@/services/api/client"
import { formatDate } from "@/lib/utils"

export default function LibraryPage() {
  const studentId = useAuthStore((s) => s.studentId)
  const [query, setQuery] = useState("")
  const { data: books, isLoading: searching } = useSearchBooks(query)
  const borrowMutation = useBorrowBook()
  const returnMutation = useReturnBook()
  const { data: borrowings, isLoading: borrowingsLoading } = useMyBorrowings(studentId)

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-semibold text-ink mb-1">Library</h1>
      <p className="text-cocoa-400 mb-6">Search books, borrow, and manage your active loans.</p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader><CardTitle>Search Books</CardTitle></CardHeader>
          <CardContent>
            {borrowMutation.isError && <ErrorAlert message={getErrorMessage(borrowMutation.error)} />}
            {borrowMutation.isSuccess && <SuccessAlert message="Book borrowed successfully." />}

            <Input
              placeholder="Search by title or author..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="mb-4"
            />

            {searching && <Spinner />}

            <div className="space-y-2 max-h-96 overflow-y-auto scrollbar-thin">
              {books?.map((book) => (
                <div key={book.id} className="flex items-center justify-between border border-cocoa-100 rounded-md px-4 py-3">
                  <div>
                    <p className="font-medium text-sm">{book.title}</p>
                    <p className="text-xs text-cocoa-400">{book.author}</p>
                    <p className="text-xs text-cocoa-400 font-mono">
                      {book.available_copies}/{book.total_copies} available
                    </p>
                  </div>
                  <Button
                    size="sm"
                    disabled={book.available_copies <= 0 || !studentId}
                    isLoading={borrowMutation.isPending}
                    onClick={() =>
                      studentId &&
                      borrowMutation.mutate({ student_id: studentId, book_id: book.id, days: 14 })
                    }
                  >
                    Borrow
                  </Button>
                </div>
              ))}
              {query.length > 1 && books && books.length === 0 && (
                <p className="text-sm text-cocoa-400 text-center py-4">No books found.</p>
              )}
            </div>
            {!studentId && (
              <p className="text-xs text-cocoa-500 mt-3">
                Accept your admission offer to create a student record before borrowing books.
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>My Active Borrowings</CardTitle></CardHeader>
          <CardContent>
            {returnMutation.isError && <ErrorAlert message={getErrorMessage(returnMutation.error)} />}
            {borrowingsLoading && <Spinner />}

            <div className="space-y-2">
              {borrowings?.map((b) => (
                <div key={b.id} className="flex items-center justify-between border border-cocoa-100 rounded-md px-4 py-3">
                  <div>
                    <p className="text-sm font-medium">Book: {b.book_id.slice(0, 10)}...</p>
                    <p className="text-xs text-cocoa-400">Due: {formatDate(b.due_date)}</p>
                  </div>
                  <Button size="sm" variant="outline" isLoading={returnMutation.isPending} onClick={() => returnMutation.mutate(b.id)}>
                    Return
                  </Button>
                </div>
              ))}
              {borrowings && borrowings.length === 0 && (
                <p className="text-sm text-cocoa-400 text-center py-4">No active borrowings.</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  )
}
