import React, { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import { AppShell } from "@/components/layout/AppShell"
import { lecturerApi } from "@/services/api/lecturer"
import { getErrorMessage } from "@/services/api/client"

export default function LecturerRosterPage() {
  const { courseId } = useParams()
  const [roster, setRoster] = useState<any[]>([])
  const [error, setError] = useState<string | null>(null)
  const [qr, setQr] = useState<string | null>(null)

  async function load() {
    try {
      const res = await lecturerApi.getRoster(courseId || '')
      setRoster(res.data)
    } catch (err) {
      setError(getErrorMessage(err))
    }
  }

  async function showQr() {
    try {
      const res = await lecturerApi.generateQr(courseId || '')
      setQr(res.data.qr_image)
    } catch (err) {
      setError(getErrorMessage(err))
    }
  }

  async function mark(studentId: string, present: boolean) {
    try {
      await lecturerApi.markAttendance(courseId || '', { student_id: studentId, course_id: courseId, session_date: new Date().toISOString(), is_present: present })
      await load()
    } catch (err) {
      setError(getErrorMessage(err))
    }
  }

  useEffect(() => { load() }, [courseId])

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-semibold text-ink mb-1">Roster</h1>
      {error && <p className="text-red-500">{error}</p>}
      <div className="mb-4">
        <button className="btn btn-primary" onClick={showQr}>Generate QR for session</button>
        {qr && <div className="mt-3"><img src={qr} alt="attendance-qr" /></div>}
      </div>
      <table className="w-full table-auto">
        <thead><tr><th>Student</th><th>Email</th><th>Actions</th></tr></thead>
        <tbody>
          {roster.map(s => (
            <tr key={s.id}>
              <td>{s.student_id} — {s.name}</td>
              <td>{s.email}</td>
              <td>
                <button className="btn btn-sm mr-2" onClick={() => mark(s.student_id, true)}>Present</button>
                <button className="btn btn-sm" onClick={() => mark(s.student_id, false)}>Absent</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </AppShell>
  )
}
