import React, { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import { AppShell } from "@/components/layout/AppShell"
import { lecturerApi } from "@/services/api/lecturer"
import { getErrorMessage } from "@/services/api/client"

export default function AttendanceReportPage() {
  const { courseId } = useParams()
  const [report, setReport] = useState<any | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [range, setRange] = useState({ start: new Date().toISOString().slice(0,10), end: new Date().toISOString().slice(0,10) })

  async function load() {
    try {
      const res = await lecturerApi.getReport(courseId || '', range.start, range.end)
      setReport(res.data)
    } catch (err) {
      setError(getErrorMessage(err))
    }
  }

  useEffect(() => { load() }, [])

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-semibold text-ink mb-1">Attendance Report</h1>
      {error && <p className="text-red-500">{error}</p>}
      <div className="mb-4">
        <label className="mr-2">Start</label>
        <input type="date" value={range.start} onChange={(e)=> setRange({...range, start: e.target.value})} />
        <label className="ml-4 mr-2">End</label>
        <input type="date" value={range.end} onChange={(e)=> setRange({...range, end: e.target.value})} />
        <button className="btn btn-sm ml-4" onClick={load}>Load</button>
      </div>

      {report && (
        <div>
          <div>Total sessions: {report.total_sessions}</div>
          <table className="w-full table-auto mt-3">
            <thead><tr><th>Student ID</th><th>Present</th><th>Total</th><th>Percent</th></tr></thead>
            <tbody>
              {report.report.map((r: any)=> (
                <tr key={r.student_id}><td>{r.student_id}</td><td>{r.present}</td><td>{r.total}</td><td>{r.percent.toFixed(1)}%</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </AppShell>
  )
}
