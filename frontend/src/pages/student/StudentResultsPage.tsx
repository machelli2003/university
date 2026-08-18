import { useEffect, useState } from "react"
import { AppShell } from "@/components/layout/AppShell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { studentApi } from "@/services/api/student"

export default function StudentResultsPage() {
  const [results, setResults] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function load() {
      setLoading(true)
      setError(null)
      try {
        const res = await studentApi.results()
        setResults(res.data)
      } catch (err: any) {
        setError(
          err?.response?.data?.detail ||
          err?.message ||
          "Failed to load results"
        )
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const gradeColor = (grade: string) => {
    if (!grade) return "text-cocoa-500"
    if (grade.startsWith("A")) return "text-green-600"
    if (grade.startsWith("B")) return "text-blue-600"
    if (grade.startsWith("C")) return "text-yellow-600"
    if (grade.startsWith("D")) return "text-orange-600"
    return "text-red-600"
  }

  if (loading) {
    return (
      <AppShell>
        <div className="space-y-6">
          <h1 className="font-display text-2xl font-semibold text-ink mb-1">Exam Results</h1>
          <p className="text-cocoa-500 animate-pulse">Loading results…</p>
        </div>
      </AppShell>
    )
  }

  if (error) {
    return (
      <AppShell>
        <div className="space-y-4">
          <h1 className="font-display text-2xl font-semibold text-ink mb-1">Exam Results</h1>
          <div className="rounded-lg border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">
            <p className="font-semibold">Could not load results</p>
            <p>{error}</p>
          </div>
        </div>
      </AppShell>
    )
  }

  const courses: any[] = results?.courses ?? []
  const hasCourses = courses.length > 0

  const totalCredits = courses.reduce((sum: number, c: any) => sum + (c.credits || 0), 0)

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
          <div>
            <h1 className="font-display text-2xl font-semibold text-ink mb-1">Exam Results</h1>
            {results && (
              <p className="text-cocoa-400">
                {results.academic_year} — Semester {results.semester}
              </p>
            )}
          </div>
          {hasCourses && <Button variant="outline">Download transcript</Button>}
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader><CardTitle className="text-sm">Current GPA</CardTitle></CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-600">
                {results?.gpa != null ? Number(results.gpa).toFixed(2) : "—"}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle className="text-sm">CGPA</CardTitle></CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-600">
                {results?.cgpa != null ? Number(results.cgpa).toFixed(2) : "—"}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle className="text-sm">Courses Taken</CardTitle></CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600">{courses.length}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle className="text-sm">Total Credits</CardTitle></CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-purple-600">{totalCredits}</div>
            </CardContent>
          </Card>
        </div>

        {/* Results table */}
        <Card>
          <CardHeader><CardTitle>Course Results</CardTitle></CardHeader>
          <CardContent>
            {!hasCourses ? (
              <div className="text-center py-12 text-cocoa-400">
                <p className="text-lg mb-2">No results yet</p>
                <p className="text-sm">
                  Grades will appear here once your lecturers submit and they are approved.
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-cocoa-100 text-left text-cocoa-500">
                      <th className="px-3 py-2 font-medium">Course Code</th>
                      <th className="px-3 py-2 font-medium">Course Name</th>
                      <th className="px-3 py-2 font-medium">Score</th>
                      <th className="px-3 py-2 font-medium">Grade</th>
                      <th className="px-3 py-2 font-medium">Credits</th>
                      <th className="px-3 py-2 font-medium">GPA Points</th>
                    </tr>
                  </thead>
                  <tbody>
                    {courses.map((course: any) => (
                      <tr key={course.course_id} className="border-b border-cocoa-50 hover:bg-cocoa-50/30 transition-colors">
                        <td className="px-3 py-3 font-medium text-ink">{course.course_code}</td>
                        <td className="px-3 py-3 text-cocoa-600 max-w-xs truncate">{course.course_name}</td>
                        <td className="px-3 py-3 font-mono">{Number(course.score).toFixed(1)}</td>
                        <td className={`px-3 py-3 font-semibold ${gradeColor(course.grade)}`}>{course.grade}</td>
                        <td className="px-3 py-3 font-mono">{course.credits}</td>
                        <td className="px-3 py-3 font-mono">{Number(course.gpa_points).toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </AppShell>
  )
}
