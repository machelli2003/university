import React, { useEffect, useState } from "react"
import { AppShell } from "@/components/layout/AppShell"
import { studentApi } from "@/services/api/student"
import { Link } from "react-router-dom"
import { Button } from "@/components/ui/Button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"

type Tab = "overview" | "courses" | "progress" | "results" | "payments"

export default function StudentDashboardPage() {
  const [data, setData] = useState<any | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [tab, setTab] = useState<Tab>("overview")

  useEffect(() => {
    async function load() {
      setLoading(true)
      setError(null)
      try {
        const res = await studentApi.me()
        setData(res.data)
      } catch (err: any) {
        const msg =
          err?.response?.data?.detail ||
          err?.message ||
          "Failed to load student data"
        setError(msg)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) {
    return (
      <AppShell>
        <div className="flex items-center justify-center min-h-[40vh]">
          <p className="text-cocoa-500 animate-pulse">Loading student portal…</p>
        </div>
      </AppShell>
    )
  }

  if (error || !data) {
    return (
      <AppShell>
        <div className="space-y-4">
          <h1 className="font-display text-2xl font-semibold text-ink">Student Dashboard</h1>
          <div className="rounded-lg border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">
            <p className="font-semibold mb-1">Could not load your student record</p>
            <p>{error || "No data returned from the server."}</p>
            <p className="mt-2 text-xs text-red-500">
              If you were recently enrolled, please contact the Registrar's Office to ensure your account is linked to a student record.
            </p>
          </div>
        </div>
      </AppShell>
    )
  }

  const profile = data.profile
  const courses: any[] = data.courses ?? []
  const timetable: any[] = data.timetable ?? []
  const transcripts: any[] = data.transcripts ?? []
  const payments: any[] = data.payments ?? []

  const gradeColor = (grade: string) => {
    if (!grade) return "text-cocoa-500"
    if (grade.startsWith("A")) return "text-green-700"
    if (grade.startsWith("B")) return "text-blue-700"
    if (grade.startsWith("C")) return "text-yellow-700"
    if (grade.startsWith("D")) return "text-orange-700"
    return "text-red-600"
  }

  const standingLabel = (status: string) => {
    if (status === "good_standing") return "Good Standing"
    if (status === "academic_probation") return "Academic Probation"
    return "Suspended"
  }

  const standingColor = (status: string) => {
    if (status === "good_standing") return "bg-green-50 text-green-700"
    if (status === "academic_probation") return "bg-amber-50 text-amber-700"
    return "bg-red-50 text-red-700"
  }

  return (
    <AppShell>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
          <div>
            <h1 className="font-display text-2xl font-semibold text-ink mb-1">
              Welcome back, {profile.first_name} {profile.last_name}
            </h1>
            <p className="text-cocoa-400">
              {profile.student_id}
              {profile.programme_id && ` • ${profile.programme_id}`}
              {profile.level && ` • ${profile.level}`}
            </p>
          </div>
          <Link to="/academic/registration">
            <Button>Register Courses</Button>
          </Link>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader><CardTitle>CGPA</CardTitle></CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-600">
                {profile.cgpa != null ? Number(profile.cgpa).toFixed(2) : "—"}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Registered Courses</CardTitle></CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600">{courses.length}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Fee Balance</CardTitle></CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-orange-600">
                GHS {Number(profile.fee_balance ?? 0).toFixed(2)}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Academic Year</CardTitle></CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-600">
                {profile.academic_year || "—"}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick-link service cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
          <Card>
            <CardHeader><CardTitle>Fees &amp; Payments</CardTitle></CardHeader>
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

        {/* Tabs */}
        <div className="rounded-xl border border-cocoa-100 bg-white p-1 inline-flex gap-1 flex-wrap">
          {(["overview", "courses", "progress", "results", "payments"] as Tab[]).map((item) => (
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

        {/* ── Overview ── */}
        {tab === "overview" && (
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            <Card>
              <CardHeader><CardTitle>Current Courses</CardTitle></CardHeader>
              <CardContent>
                {courses.length === 0 ? (
                  <p className="text-sm text-cocoa-400">No courses registered yet. <Link to="/academic/registration" className="text-blue-600 underline">Register now</Link>.</p>
                ) : (
                  <div className="space-y-3">
                    {courses.map((course: any) => (
                      <div key={course.course_id} className="flex items-center justify-between rounded border border-cocoa-100 p-3">
                        <div>
                          <div className="font-medium text-ink">{course.code}</div>
                          <div className="text-sm text-cocoa-500">{course.name}</div>
                        </div>
                        {course.grade ? (
                          <span className={`rounded px-2 py-1 text-xs font-semibold bg-blue-50 ${gradeColor(course.grade)}`}>
                            {course.grade}
                          </span>
                        ) : (
                          <span className="rounded bg-green-50 px-2 py-1 text-xs font-semibold text-green-700">Active</span>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader><CardTitle>Timetable</CardTitle></CardHeader>
              <CardContent>
                {timetable.length === 0 ? (
                  <p className="text-sm text-cocoa-400">No timetable data available.</p>
                ) : (
                  <div className="space-y-3">
                    {timetable.map((slot: any, index: number) => (
                      <div key={`${slot.day}-${index}`} className="flex items-center justify-between rounded border border-cocoa-100 p-3">
                        <div>
                          <div className="font-medium text-ink">{slot.day}</div>
                          <div className="text-sm text-cocoa-500">{slot.time}</div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-medium text-cocoa-700">{slot.course}</div>
                          {slot.room && slot.room !== "TBA" && (
                            <div className="text-xs text-cocoa-400">{slot.room}</div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {/* ── Courses ── */}
        {tab === "courses" && (
          <Card>
            <CardHeader><CardTitle>Course List</CardTitle></CardHeader>
            <CardContent>
              {courses.length === 0 ? (
                <div className="text-center py-10 text-cocoa-400">
                  <p className="text-lg mb-2">No courses registered</p>
                  <p className="text-sm mb-4">Head to course registration to enrol for this semester.</p>
                  <Link to="/academic/registration"><Button>Register Courses</Button></Link>
                </div>
              ) : (
                <div className="space-y-3">
                  {courses.map((course: any) => (
                    <div key={course.course_id} className="flex items-center justify-between rounded border border-cocoa-100 p-4">
                      <div>
                        <p className="font-medium text-ink">{course.code} — {course.name}</p>
                        <p className="text-sm text-cocoa-500">{course.credit_hours} credit hours</p>
                      </div>
                      {course.grade ? (
                        <span className={`rounded px-2 py-1 text-xs font-semibold bg-blue-50 ${gradeColor(course.grade)}`}>
                          {course.grade}
                        </span>
                      ) : (
                        <span className="rounded bg-green-50 px-2 py-1 text-xs font-semibold text-green-700">Active</span>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* ── Progress ── */}
        {tab === "progress" && (
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            <Card>
              <CardHeader><CardTitle>Academic Standing</CardTitle></CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between rounded border border-cocoa-100 p-4">
                    <div>
                      <div className="text-sm text-cocoa-500">Current CGPA</div>
                      <div className="text-3xl font-bold text-ink">
                        {profile.cgpa != null ? Number(profile.cgpa).toFixed(2) : "—"}
                      </div>
                    </div>
                    <span className={`rounded px-3 py-1 text-xs font-semibold ${standingColor(profile.status || "")}`}>
                      {standingLabel(profile.status || "")}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="rounded border border-cocoa-100 p-3">
                      <div className="text-cocoa-500">Credits earned</div>
                      <div className="mt-1 text-xl font-bold text-ink">
                        {courses.reduce((sum: number, c: any) => sum + (c.credit_hours || 3), 0)}
                      </div>
                    </div>
                    <div className="rounded border border-cocoa-100 p-3">
                      <div className="text-cocoa-500">Programme level</div>
                      <div className="mt-1 text-xl font-bold text-ink">{profile.level || "—"}</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader><CardTitle>Transcript History</CardTitle></CardHeader>
              <CardContent>
                {transcripts.length === 0 ? (
                  <p className="text-sm text-cocoa-400">No transcripts generated yet.</p>
                ) : (
                  <div className="space-y-3">
                    {transcripts.map((t: any, idx: number) => (
                      <div key={`${t.academic_year}-${t.semester}-${idx}`} className="rounded border border-cocoa-100 p-4">
                        <div className="flex items-center justify-between mb-2">
                          <div>
                            <div className="font-semibold text-ink">{t.academic_year}</div>
                            <div className="text-sm text-cocoa-500">Semester {t.semester}</div>
                          </div>
                          {t.cgpa != null && (
                            <span className="rounded bg-purple-50 px-2 py-1 text-xs font-semibold text-purple-700">
                              CGPA {Number(t.cgpa).toFixed(2)}
                            </span>
                          )}
                        </div>
                        <div className="text-xs text-cocoa-400">{(t.courses || []).length} course(s) recorded</div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {/* ── Results ── */}
        {tab === "results" && (
          <Card>
            <CardHeader><CardTitle>Latest Results</CardTitle></CardHeader>
            <CardContent>
              {transcripts.length === 0 ? (
                <div className="text-center py-10 text-cocoa-400">
                  <p className="text-lg mb-2">No results yet</p>
                  <p className="text-sm">Grades will appear here once your lecturer submits them.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {transcripts.map((result: any, idx: number) => (
                    <div key={`${result.academic_year}-${result.semester}-${idx}`} className="rounded border border-cocoa-100 p-4">
                      <div className="mb-3 flex items-center justify-between">
                        <div>
                          <div className="font-semibold text-ink">{result.academic_year}</div>
                          <div className="text-sm text-cocoa-500">Semester {result.semester}</div>
                        </div>
                        {result.cgpa != null && (
                          <span className="rounded bg-purple-50 px-2 py-1 text-xs font-semibold text-purple-700">
                            CGPA {Number(result.cgpa).toFixed(2)}
                          </span>
                        )}
                      </div>
                      <div className="space-y-2">
                        {(result.courses || []).map((course: any, ci: number) => (
                          <div key={`${course.course_id || ci}`} className="flex items-center justify-between text-sm">
                            <span>{course.course_code || course.course_id} — {course.course_name || ""}</span>
                            <span className={`font-medium ${gradeColor(course.grade || course.letter_grade || "")}`}>
                              {course.grade || course.letter_grade || "N/A"}
                            </span>
                          </div>
                        ))}
                        {(result.courses || []).length === 0 && (
                          <p className="text-xs text-cocoa-400">No course entries for this period.</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* ── Payments ── */}
        {tab === "payments" && (
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Payments</CardTitle>
                <Link to="/finance/payments">
                  <Button variant="outline" className="text-xs">View all</Button>
                </Link>
              </div>
            </CardHeader>
            <CardContent>
              {payments.length === 0 ? (
                <div className="text-center py-10 text-cocoa-400">
                  <p className="text-lg mb-2">No payment records</p>
                  <p className="text-sm mb-4">Make your first payment to see it here.</p>
                  <Link to="/finance/payments"><Button>Go to Payments</Button></Link>
                </div>
              ) : (
                <div className="space-y-3">
                  {payments.map((payment: any) => (
                    <div key={payment.id} className="flex items-center justify-between rounded border border-cocoa-100 p-4">
                      <div>
                        <div className="font-medium text-ink">{payment.id}</div>
                        <div className="text-sm text-cocoa-500">{payment.payment_date || "—"}</div>
                      </div>
                      <div className="text-right">
                        <div className="font-medium text-ink">GHS {Number(payment.amount || 0).toFixed(2)}</div>
                        <div
                          className={`text-xs font-semibold ${
                            String(payment.status).toLowerCase() === "success"
                              ? "text-green-700"
                              : "text-amber-700"
                          }`}
                        >
                          {payment.status}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </AppShell>
  )
}
