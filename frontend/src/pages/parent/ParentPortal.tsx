import React, { useState } from "react"
import { AppShell } from "@/components/layout/AppShell"
import { useLinkStudent, useLinkedStudents } from "@/hooks/useParents"
import { useToast } from "@/components/ui/Toast"
import { getErrorMessage } from "@/services/api/client"

export default function ParentPortal() {
  const [studentId, setStudentId] = useState("")
  const link = useLinkStudent()
  const { data: students, refetch } = useLinkedStudents()
  const [error, setError] = useState<string | null>(null)
  const toast = useToast()

  async function handleLink(e: React.FormEvent) {
    e.preventDefault()
    try {
      if (!studentId) throw new Error('Student ID required')
      await link.mutateAsync(studentId)
      setStudentId("")
      refetch()
    } catch (err) {
      const msg = getErrorMessage(err)
      setError(msg)
      toast.show({ message: msg, type: 'error' })
    }
  }

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-semibold text-ink mb-2">Parent / Guardian Portal</h1>
      {error && <div className="text-red-500">{error}</div>}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <h2 className="font-semibold mb-2">Link a Student</h2>
          <form onSubmit={handleLink} className="flex gap-2">
            <input value={studentId} onChange={(e)=> setStudentId(e.target.value)} placeholder="Student ID" className="input" />
            <button className="btn btn-primary" type="submit">Link</button>
          </form>
        </div>

        <div>
          <h2 className="font-semibold mb-2">Linked Students</h2>
          <div className="space-y-2">
            {students?.map((s: any) => (
              <div key={s.student_id} className="border p-3 rounded">
                <div className="font-medium">{s.first_name} {s.last_name}</div>
                <div className="text-sm text-cocoa-400">ID: {s.student_id} — {s.email}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </AppShell>
  )
}
