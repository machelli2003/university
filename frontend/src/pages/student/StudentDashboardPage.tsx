import React, { useEffect, useState } from "react"
import { AppShell } from "@/components/layout/AppShell"
import { studentApi } from "@/services/api/student"
import { getErrorMessage } from "@/services/api/client"
import { Link } from "react-router-dom"
import { Button } from "@/components/ui/Button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"

const fallbackStudentData = {
  profile: {
    first_name: "Akwasi",
    last_name: "Mensah",
    student_id: "STD-2025-0142",
    programme_id: "BSc Computer Science",
    fee_balance: 1240.0,
    cgpa: 3.74,
    level: "Level 200",
    academic_year: "2025/2026",
  },
  courses: [
    { code: "CS101", title: "Introduction to Programming", grade: "A", lecturer: "Dr. Osei" },
    { code: "MTH201", title: "Calculus II", grade: "B+", lecturer: "Dr. Yeboah" },
    { code: "ENG200", title: "Academic Writing", grade: "A-", lecturer: "Prof. Adams" },
  ],
  timetable: [
    { day: "Monday", time: "09:00-11:00", course: "CS101" },
    { day: "Tuesday", time: "11:00-13:00", course: "MTH201" },
    { day: "Wednesday", time: "14:00-16:00", course: "ENG200" },
  ],
  payments: [
    { id: "INV-101", amount: "GHS 4000", status: "Paid", payment_date: "2025-08-01" },
    { id: "INV-102", amount: "GHS 1800", status: "Pending", payment_date: "2025-09-15" },
  ],
  transcripts: [
    {
      academic_year: "2025/2026",
      semester: "Semester 1",
      cgpa: 3.74,
      courses: [
        { code: "CS101", title: "Introduction to Programming", grade: "A" },
        { code: "MTH201", title: "Calculus II", grade: "B+" },
        { code: "ENG200", title: "Academic Writing", grade: "A-" },
      ],
    },
  ],
}

export default function StudentDashboardPage() {
  const [data, setData] = useState<any | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [tab, setTab] = useState<"overview" | "courses" | "progress" | "results" | "payments">("overview")

  async function load() {
    setLoading(true)
    try {
      const res = await studentApi.me()
      setData(res.data)
    } catch (err) {
      setError(getErrorMessage(err))
      setData(fallbackStudentData)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const student = data ?? fallbackStudentData

  if (loading && !data) {
    return (
      <AppShell>
        <div className="flex items-center justify-center min-h-[40vh]">
          <p className="text-cocoa-500">Loading student portal...</p>
        </div>
      </AppShell>
    )
  }

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
          <div>
            <h1 className="font-display text-2xl font-semibold text-ink mb-1">
              Welcome back, {student.profile.first_name} {student.profile.last_name}
            </h1>
            <p className="text-cocoa-400">
              {student.profile.student_id} • {student.profile.programme_id} • {student.profile.level}
            </p>
          </div>
          <Link to="/academic/registration">
            <Button>Register Courses</Button>
          </Link>
        </div>

        {error && (
          <div className="rounded border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-700">
            {error} — showing the student workspace with sample data.
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader><CardTitle>CGPA</CardTitle></CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-600">{student.profile.cgpa ?? "3.74"}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Registered Courses</CardTitle></CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600">{student.courses.length}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Fee Balance</CardTitle></CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-orange-600">GHS {Number(student.profile.fee_balance ?? 0).toFixed(2)}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Academic Year</CardTitle></CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-600">{student.profile.academic_year ?? "2025/2026"}</div>
            </CardContent>
          </Card>
        </div>

        <div className="rounded-xl border border-cocoa-100 bg-white p-1 inline-flex gap-1">
          {(["overview", "courses", "progress", "results", "payments"] as const).map((item) => (
            <button
              key={item}
              onClick={() => setTab(item)}
              className={`rounded-lg px-4 py-2 text-sm font-medium capitalize ${
                tab === item ? "bg-cocoa-900 text-white" : "text-cocoa-500 hover:bg-cocoa-50"
              }`}
            >
              {item}
            </button>
          ))}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
          <Card>
            <CardHeader><CardTitle>Fees & Payments</CardTitle></CardHeader>
            <CardContent>
              <p className="text-sm text-cocoa-500 mb-4">Pay tuition, view balance, and review payment history.</p>
              <Link to="/finance/payments"><Button>Open payments</Button></Link>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Library</CardTitle></CardHeader>
            <CardContent>
              <p className="text-sm text-cocoa-500 mb-4">Borrow books and manage active library loans.</p>
              <Link to="/library"><Button>Visit library</Button></Link>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Health Services</CardTitle></CardHeader>
            <CardContent>
              <p className="text-sm text-cocoa-500 mb-4">Update health details, appointments, and counseling requests.</p>
              <Link to="/health"><Button>Open health</Button></Link>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Documents</CardTitle></CardHeader>
            <CardContent>
              <p className="text-sm text-cocoa-500 mb-4">Upload and verify your academic and identity documents.</p>
              <Link to="/documents"><Button>View documents</Button></Link>
            </CardContent>
          </Card>
        </div>

        {tab === "overview" && (
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            <Card>
              <CardHeader><CardTitle>Current Courses</CardTitle></CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {student.courses.map((course: any) => (
                    <div key={course.code} className="flex items-center justify-between rounded border border-cocoa-100 p-3">
                      <div>
                        <div className="font-medium text-ink">{course.code}</div>
                        <div className="text-sm text-cocoa-500">{course.title}</div>
                      </div>
                      <span className="rounded bg-blue-50 px-2 py-1 text-xs font-semibold text-blue-700">{course.grade}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader><CardTitle>Timetable</CardTitle></CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {student.timetable.map((item: any, index: number) => (
                    <div key={`${item.day}-${index}`} className="flex items-center justify-between rounded border border-cocoa-100 p-3">
                      <div>
                        <div className="font-medium text-ink">{item.day}</div>
                        <div className="text-sm text-cocoa-500">{item.time}</div>
                      </div>
                      <span className="text-sm font-medium text-cocoa-700">{item.course}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {tab === "courses" && (
          <Card>
            <CardHeader><CardTitle>Course List</CardTitle></CardHeader>
            <CardContent>
              <div className="space-y-3">
                {student.courses.map((course: any) => (
                  <div key={course.code} className="flex items-center justify-between rounded border border-cocoa-100 p-4">
                    <div>
                      <p className="font-medium text-ink">{course.code} — {course.title}</p>
                      <p className="text-sm text-cocoa-500">Lecturer: {course.lecturer}</p>
                    </div>
                    <span className="rounded bg-green-50 px-2 py-1 text-xs font-semibold text-green-700">Active</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {tab === "progress" && (
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            <Card>
              <CardHeader><CardTitle>Academic Standing</CardTitle></CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between rounded border border-cocoa-100 p-4">
                    <div>
                      <div className="text-sm text-cocoa-500">Current CGPA</div>
                      <div className="text-3xl font-bold text-ink">{student.profile.cgpa ?? "3.74"}</div>
                    </div>
                    <span className="rounded bg-green-50 px-3 py-1 text-xs font-semibold text-green-700">Good Standing</span>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="rounded border border-cocoa-100 p-3">
                      <div className="text-cocoa-500">Credits earned</div>
                      <div className="mt-1 text-xl font-bold text-ink">{student.courses.length * 3}</div>
                    </div>
                    <div className="rounded border border-cocoa-100 p-3">
                      <div className="text-cocoa-500">Programme level</div>
                      <div className="mt-1 text-xl font-bold text-ink">{student.profile.level}</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader><CardTitle>Progression Plan</CardTitle></CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="rounded border border-cocoa-100 p-4">
                    <div className="text-sm text-cocoa-500 mb-2">Next milestone</div>
                    <div className="font-semibold text-ink">Complete required credits for Level 300 progression</div>
                  </div>
                  <div className="rounded border border-cocoa-100 p-4">
                    <div className="text-sm text-cocoa-500 mb-2">Recommended action</div>
                    <div className="text-ink">Maintain current GPA and complete the remaining core courses in your registration plan.</div>
                  </div>
                  <button
                    onClick={() => {
                      const transcript = student.transcripts
                        .map((result: any) => `${result.academic_year} ${result.semester}\n${result.courses.map((course: any) => `${course.code}: ${course.title} - ${course.grade}`).join("\n")}`)
                        .join("\n\n")

                      const blob = new Blob([`Student Transcript\n\n${transcript}`], { type: "text/plain;charset=utf-8" })
                      const url = URL.createObjectURL(blob)
                      const link = document.createElement("a")
                      link.href = url
                      link.download = `${student.profile.student_id || "student"}-transcript.txt`
                      link.click()
                      URL.revokeObjectURL(url)
                    }}
                    className="w-full rounded-md bg-cocoa-900 px-4 py-2 text-sm font-medium text-white hover:bg-cocoa-800"
                  >
                    Download transcript
                  </button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {tab === "results" && (
          <Card>
            <CardHeader><CardTitle>Latest Results</CardTitle></CardHeader>
            <CardContent>
              <div className="space-y-4">
                {student.transcripts.map((result: any) => (
                  <div key={`${result.academic_year}-${result.semester}`} className="rounded border border-cocoa-100 p-4">
                    <div className="mb-3 flex items-center justify-between">
                      <div>
                        <div className="font-semibold text-ink">{result.academic_year}</div>
                        <div className="text-sm text-cocoa-500">{result.semester}</div>
                      </div>
                      <span className="rounded bg-purple-50 px-2 py-1 text-xs font-semibold text-purple-700">CGPA {result.cgpa}</span>
                    </div>
                    <div className="space-y-2">
                      {result.courses.map((course: any) => (
                        <div key={course.code} className="flex items-center justify-between text-sm">
                          <span>{course.code} — {course.title}</span>
                          <span className="font-medium text-cocoa-700">{course.grade}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {tab === "payments" && (
          <Card>
            <CardHeader><CardTitle>Payments</CardTitle></CardHeader>
            <CardContent>
              <div className="space-y-3">
                {student.payments.map((payment: any) => (
                  <div key={payment.id} className="flex items-center justify-between rounded border border-cocoa-100 p-4">
                    <div>
                      <div className="font-medium text-ink">{payment.id}</div>
                      <div className="text-sm text-cocoa-500">{payment.payment_date}</div>
                    </div>
                    <div className="text-right">
                      <div className="font-medium text-ink">{payment.amount}</div>
                      <div className={`text-xs font-semibold ${payment.status === "Paid" ? "text-green-700" : "text-amber-700"}`}>
                        {payment.status}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </AppShell>
  )
}
