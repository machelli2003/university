import { AppShell } from "@/components/layout/AppShell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { studentApi } from "@/services/api/student"
import { useEffect, useState } from "react"

export default function TimetablePage() {
  const [timetable, setTimetable] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    async function load() {
      setLoading(true)
      try {
        const data = await studentApi.timetable()
        setTimetable(data)
      } finally {
        setLoading(false)
      }
    }

    load()
  }, [])

  if (loading) {
    return (
      <AppShell>
        <div className="space-y-6">
          <h1 className="font-display text-2xl font-semibold text-ink mb-1">My Timetable</h1>
          <p className="text-cocoa-500">Loading timetable...</p>
        </div>
      </AppShell>
    )
  }

  if (!timetable) {
    return (
      <AppShell>
        <div className="space-y-6">
          <h1 className="font-display text-2xl font-semibold text-ink mb-1">My Timetable</h1>
          <p className="text-cocoa-500">No timetable data available.</p>
        </div>
      </AppShell>
    )
  }

  // Build a schedule organized by day
  const scheduleByDay: Record<string, any[]> = {}
  timetable.courses?.forEach((course: any) => {
    course.schedule?.forEach((slot: any) => {
      if (!scheduleByDay[slot.day]) {
        scheduleByDay[slot.day] = []
      }
      scheduleByDay[slot.day].push({
        ...slot,
        course_code: course.course_code,
        course_name: course.course_name,
        credits: course.credits,
      })
    })
  })

  // Sort days in order
  const dayOrder = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
  const sortedDays = Object.keys(scheduleByDay).sort((a, b) => dayOrder.indexOf(a) - dayOrder.indexOf(b))

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex items-center justify-between gap-4">
          <div>
            <h1 className="font-display text-2xl font-semibold text-ink mb-1">My Timetable</h1>
            <p className="text-cocoa-400">
              {timetable.academic_year} - Semester {timetable.semester}
            </p>
          </div>
          <Button variant="outline">Export schedule</Button>
        </div>

        <div className="space-y-4">
          {sortedDays.map((day) => (
            <Card key={day}>
              <CardHeader>
                <CardTitle className="text-lg">{day}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {scheduleByDay[day].map((slot, index) => (
                    <div
                      key={`${day}-${slot.course_code}-${index}`}
                      className="flex items-start justify-between rounded border border-cocoa-100 p-4 hover:bg-cocoa-50 transition-colors"
                    >
                      <div className="flex-1">
                        <div className="font-semibold text-ink">{slot.course_code}</div>
                        <div className="text-sm text-cocoa-600">{slot.course_name}</div>
                        <div className="text-xs text-cocoa-500 mt-1">
                          {slot.start_time} - {slot.end_time}
                        </div>
                      </div>
                      <div className="text-right ml-4">
                        <div className="text-sm font-medium text-ink">{slot.room}</div>
                        <div className="text-xs text-cocoa-500">{slot.lecturer || "TBA"}</div>
                        <div className="text-xs text-cocoa-400 mt-1">{slot.credits} credits</div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </AppShell>
  )
}
