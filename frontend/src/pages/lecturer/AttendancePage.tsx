import React, { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import { AppShell } from "@/components/layout/AppShell"
import { lecturerApi } from "@/services/api/lecturer"
import { getErrorMessage } from "@/services/api/client"
import { Spinner } from "@/components/ui/Feedback"

export default function AttendancePage() {
  const { courseId } = useParams()
  const [roster, setRoster] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [studentsCsv, setStudentsCsv] = useState("")

  async function loadRoster() {
    setError(null)
    setLoading(true)
    try {
      const res = await lecturerApi.getRoster(courseId || "")
      setRoster(res.data)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  async function mark(studentId: string, present: boolean) {
    setMessage(null)
    setError(null)
    try {
      await lecturerApi.markAttendance(courseId || '', {
        student_id: studentId,
        course_id: courseId,
        session_date: new Date().toISOString(),
        is_present: present,
      })
      setMessage(`Marked ${studentId} as ${present ? 'present' : 'absent'}`)
      await loadRoster()
    } catch (err) {
      setError(getErrorMessage(err))
    }
  }

  async function handleMarkCsv() {
    setMessage(null)
    setError(null)
    try {
      const rows = studentsCsv.split('\n').map(r => r.trim()).filter(Boolean)
      for (const row of rows) {
        const [student_id, is_present] = row.split(',').map(s => s.trim())
        await lecturerApi.markAttendance(courseId || '', {
          student_id,
          course_id: courseId,
          session_date: new Date().toISOString(),
          is_present: is_present === 'true',
        })
      }
      setMessage('Attendance marked')
      setStudentsCsv("")
      await loadRoster()
    } catch (err) {
      setError(getErrorMessage(err))
    }
  }

  useEffect(() => { if (courseId) loadRoster() }, [courseId])

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-semibold text-ink mb-1">Attendance</h1>
      {error && <p className="text-red-500 mb-4">{error}</p>}
      {message && <p className="text-green-600 mb-4">{message}</p>}

      {loading ? (
        <div className="flex justify-center py-16"><Spinner className="h-8 w-8" /></div>
      ) : roster.length > 0 ? (
        <div className="space-y-4">
          <div className="text-cocoa-400">Mark attendance for each student below. You can also use the roster page for QR and full roster management.</div>
          <table className="w-full table-auto border-collapse border border-cocoa-200">
            <thead className="bg-cocoa-50 text-left text-cocoa-500">
              <tr>
                <th className="px-4 py-3">Student ID</th>
                <th className="px-4 py-3">Name</th>
                <th className="px-4 py-3">Email</th>
                <th className="px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {roster.map((student) => (
                <tr key={student.id} className="border-t border-cocoa-200">
                  <td className="px-4 py-3 font-mono text-cocoa-500">{student.student_id}</td>
                  <td className="px-4 py-3">{student.name}</td>
                  <td className="px-4 py-3">{student.email}</td>
                  <td className="px-4 py-3 space-x-2">
                    <button className="btn btn-sm" onClick={() => mark(student.student_id, true)}>Present</button>
                    <button className="btn btn-sm btn-secondary" onClick={() => mark(student.student_id, false)}>Absent</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="space-y-4">
          <p className="text-cocoa-400">No registered students were found for this course. Use CSV input below to mark attendance manually.</p>
          <textarea value={studentsCsv} onChange={(e) => setStudentsCsv(e.target.value)} className="w-full h-40 input" />
          <div className="mt-3">
            <button className="btn btn-primary" onClick={handleMarkCsv}>Mark Attendance</button>
          </div>
        </div>
      )}
    </AppShell>
  )
}
