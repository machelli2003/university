import React, { useState } from "react"
import { useParams } from "react-router-dom"
import { AppShell } from "@/components/layout/AppShell"
import axios from "axios"

export default function PublicAttendanceForm() {
  const { courseId, sessionId } = useParams()
  const [studentId, setStudentId] = useState("")
  const [message, setMessage] = useState<string | null>(null)

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setMessage(null)
    try {
      const res = await axios.post(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/attendance/mark/${courseId}/${sessionId}/public`, { student_id: studentId })
      setMessage('Attendance recorded. Thank you.')
    } catch (err: any) {
      setMessage(err.response?.data?.detail || 'Failed')
    }
  }

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-semibold text-ink mb-1">Record Attendance</h1>
      <p className="text-cocoa-400 mb-4">If you cannot login, enter your Student ID below to record attendance.</p>
      <form onSubmit={submit} className="space-y-3">
        <input value={studentId} onChange={(e)=> setStudentId(e.target.value)} placeholder="Student ID" className="w-full input" />
        <button className="btn btn-primary" type="submit">Submit</button>
      </form>
      {message && <p className="mt-3">{message}</p>}
    </AppShell>
  )
}
