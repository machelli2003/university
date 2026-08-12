import React, { useEffect, useState } from "react"
import { AppShell } from "@/components/layout/AppShell"
import { studentApi } from "@/services/api/student"
import { getErrorMessage } from "@/services/api/client"

export default function StudentDashboardPage() {
  const [data, setData] = useState<any | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function load() {
    setLoading(true)
    try {
      const res = await studentApi.me()
      setData(res.data)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  if (loading) return <AppShell><p>Loading...</p></AppShell>
  if (error) return <AppShell><p className="text-red-500">{error}</p></AppShell>

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-semibold text-ink mb-1">My Student Dashboard</h1>
      {data && (
        <div>
          <p className="mb-2">Name: {data.profile.first_name} {data.profile.last_name}</p>
          <p className="mb-2">Student ID: {data.profile.student_id}</p>
          <p className="mb-2">Programme: {data.profile.programme_id}</p>
          <p className="mb-2">Fee balance: GHS {data.profile.fee_balance.toFixed(2)}</p>

          <h2 className="mt-6 font-semibold">Transcripts</h2>
          {data.transcripts.length === 0 ? (
            <p>No transcripts available</p>
          ) : (
            data.transcripts.map((t: any) => (
              <div key={`${t.academic_year}-${t.semester}`} className="mb-4 border p-3 rounded">
                <div className="text-sm text-cocoa-500 mb-2">{t.academic_year} — {t.semester}</div>
                <div>CGPA: {t.cgpa ?? "—"}</div>
                <div className="mt-2">
                  <table className="w-full table-auto">
                    <thead>
                      <tr><th>Code</th><th>Title</th><th>Grade</th></tr>
                    </thead>
                    <tbody>
                      {t.courses.map((c: any) => (
                        <tr key={c.code}><td>{c.code}</td><td>{c.title}</td><td>{c.grade}</td></tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ))
          )}

          <h2 className="mt-6 font-semibold">Payments</h2>
          {data.payments.length === 0 ? (
            <p>No payments yet</p>
          ) : (
            <table className="w-full table-auto">
              <thead><tr><th>Amount</th><th>Status</th><th>Date</th></tr></thead>
              <tbody>
                {data.payments.map((p: any) => (
                  <tr key={p.id}><td>{p.amount}</td><td>{p.status}</td><td>{new Date(p.payment_date).toLocaleString()}</td></tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </AppShell>
  )
}
