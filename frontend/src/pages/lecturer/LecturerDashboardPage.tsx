import React, { useEffect, useState } from "react"
import { AppShell } from "@/components/layout/AppShell"
import { lecturerApi } from "@/services/api/lecturer"
import { Link } from "react-router-dom"
import { ROUTES } from "@/constants/routes"

export default function LecturerDashboardPage() {
  const [courses, setCourses] = useState<any[]>([])

  async function load() {
    try {
      const res = await lecturerApi.myCourses()
      setCourses(res.data)
    } catch (err) {
      console.error(err)
    }
  }

  useEffect(() => { load() }, [])

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-semibold text-ink mb-1">My Courses</h1>
      <div className="grid grid-cols-1 gap-3">
        {courses.map(c => (
          <div key={c.id} className="border p-3 rounded flex justify-between items-center">
            <div>
              <div className="font-medium">{c.code} — {c.title}</div>
            </div>
            <div>
              <Link to={`/lecturer/courses/${c.id}/attendance`} className="btn btn-sm mr-2">Attendance</Link>
              <Link to={`/lecturer/courses/${c.id}/roster`} className="btn btn-sm mr-2">Roster</Link>
              <Link to={`/lecturer/courses/${c.id}/attendance/report`} className="btn btn-sm mr-2">Report</Link>
              <Link to={`/lecturer/courses/${c.id}/materials`} className="btn btn-sm btn-secondary">Materials</Link>
            </div>
          </div>
        ))}
      </div>
    </AppShell>
  )
}
