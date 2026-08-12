import React, { useState } from "react"
import { AppShell } from "@/components/layout/AppShell"
import { useCreateBook, useSearchBooks, useBorrowBook, useReturnBook, useMyBorrowings } from "@/hooks/useLibrary"
import { useToast } from "@/components/ui/Toast"
import { getErrorMessage } from "@/services/api/client"

export default function LibrarianPage() {
  const [form, setForm] = useState({ title: "", isbn: "", author: "", publisher: "", category: "", total_copies: 1 })
  const [query, setQuery] = useState("")
  const createBook = useCreateBook()
  const { data: results } = useSearchBooks(query)
  const borrowBook = useBorrowBook()
  const returnBook = useReturnBook()
  const toast = useToast()
  const [borrowStudentId, setBorrowStudentId] = useState("")
  const [borrowDays, setBorrowDays] = useState(14)
  const [returnBorrowingId, setReturnBorrowingId] = useState("")
  const { data: myBorrowings } = useMyBorrowings(borrowStudentId || null)
  const [error, setError] = useState<string | null>(null)

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    try {
      if (!form.title || !form.author) throw new Error('Title and author are required')
      if (form.total_copies <= 0) throw new Error('Total copies must be > 0')
      await createBook.mutateAsync(form)
      setForm({ title: "", isbn: "", author: "", publisher: "", category: "", total_copies: 1 })
      toast.show({ message: 'Book added', type: 'success' })
    } catch (err) {
      const msg = getErrorMessage(err)
      setError(msg)
      toast.show({ message: msg, type: 'error' })
    }
  }

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-semibold text-ink mb-2">Librarian</h1>
      {error && <div className="text-red-500">{error}</div>}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <h2 className="font-semibold mb-2">Add Book</h2>
          <form onSubmit={handleCreate} className="space-y-2">
            <input value={form.title} onChange={(e)=> setForm({...form, title: e.target.value})} placeholder="Title" className="input w-full" />
            <input value={form.author} onChange={(e)=> setForm({...form, author: e.target.value})} placeholder="Author" className="input w-full" />
            <input value={form.isbn} onChange={(e)=> setForm({...form, isbn: e.target.value})} placeholder="ISBN" className="input w-full" />
            <input value={form.publisher} onChange={(e)=> setForm({...form, publisher: e.target.value})} placeholder="Publisher" className="input w-full" />
            <input value={form.category} onChange={(e)=> setForm({...form, category: e.target.value})} placeholder="Category" className="input w-full" />
            <input type="number" value={form.total_copies} onChange={(e)=> setForm({...form, total_copies: Number(e.target.value)})} placeholder="Total copies" className="input w-full" />
            <button className="btn btn-primary" type="submit">Add Book</button>
          </form>
        </div>

        <div>
          <h2 className="font-semibold mb-2">Search Catalog</h2>
          <div className="flex gap-2 mb-2">
            <input value={query} onChange={(e)=> setQuery(e.target.value)} placeholder="Search by title or author" className="input flex-1" />
          </div>

          <div className="space-y-2">
            {results?.map((b: any) => (
              <div key={b.id} className="border p-3 rounded">
                <div className="font-medium">{b.title}</div>
                <div className="text-sm text-cocoa-400">{b.author} — {b.available_copies}/{b.total_copies}</div>
                <div className="mt-2 flex gap-2">
                  <input value={borrowStudentId} onChange={(e)=> setBorrowStudentId(e.target.value)} placeholder="Student ID" className="input" />
                  <input type="number" value={borrowDays} onChange={(e)=> setBorrowDays(Number(e.target.value))} className="input w-28" />
                  <button className="btn" onClick={async ()=> { try { if (!borrowStudentId) throw new Error('Student ID required'); await borrowBook.mutateAsync({ student_id: borrowStudentId, book_id: b.id, days: borrowDays }); toast.show({ message: 'Borrow recorded', type: 'success' }) } catch (err) { const msg = (err as any)?.message || 'Borrow failed'; setError(msg); toast.show({ message: msg, type: 'error' }) } }}>Borrow</button>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-4 border p-3 rounded">
            <h3 className="font-semibold mb-2">Return Book</h3>
            <div className="flex gap-2">
              <input value={returnBorrowingId} onChange={(e)=> setReturnBorrowingId(e.target.value)} placeholder="Borrowing ID" className="input" />
              <button className="btn" onClick={async ()=> { try { if (!returnBorrowingId) throw new Error('Borrowing ID required'); await returnBook.mutateAsync(returnBorrowingId); setReturnBorrowingId(''); toast.show({ message: 'Return recorded', type: 'success' }) } catch (err) { const msg = (err as any)?.message || 'Return failed'; setError(msg); toast.show({ message: msg, type: 'error' }) } }}>Return</button>
            </div>
          </div>

          <div className="mt-4 border p-3 rounded">
            <h3 className="font-semibold mb-2">View Student Borrowings</h3>
            <div className="flex gap-2 mb-2">
              <input value={borrowStudentId} onChange={(e)=> setBorrowStudentId(e.target.value)} placeholder="Student ID" className="input" />
            </div>
            <div className="space-y-2">
              {myBorrowings?.map((b: any) => (
                <div key={b.id} className="border p-2 rounded">
                  <div>Borrowing ID: {b.id}</div>
                  <div className="text-sm">Book ID: {b.book_id} — Due: {new Date(b.due_date).toLocaleDateString()}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  )
}
