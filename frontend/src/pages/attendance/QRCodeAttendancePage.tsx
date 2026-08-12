import React, { useEffect, useState } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { AppShell } from "@/components/layout/AppShell"
import { apiClient } from "@/services/api/client"
import { useAuthStore } from "@/store/authStore"

export default function QRCodeAttendancePage() {
  const { courseId, sessionId } = useParams()
  const [message, setMessage] = useState<string | null>(null)
  const navigate = useNavigate()
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)

  useEffect(() => {
    async function mark() {
      if (!isAuthenticated) {
        setMessage('Please login to record attendance')
        return
      }

      try {
        const res = await apiClient.post(`/attendance/mark/${courseId}/${sessionId}`)
        setMessage('Attendance recorded — thank you')
        setTimeout(()=> navigate('/dashboard'), 1500)
      } catch (err: any) {
        setMessage((err.response?.data?.detail) || 'Failed to record attendance')
      }
    }

    mark()
  }, [courseId, sessionId, isAuthenticated])

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-semibold text-ink mb-1">Attendance</h1>
      <p>{message ?? 'Recording attendance...'}</p>
    </AppShell>
  )
}
