import { AppShell } from "@/components/layout/AppShell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { Spinner, ErrorAlert } from "@/components/ui/Feedback"
import { useMyGrades } from "@/hooks/useExam"
import { getErrorMessage } from "@/services/api/client"

export default function MyGradesPage() {
  const { data: grades, isLoading, error } = useMyGrades()

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-semibold text-ink mb-1">My Submitted Grades</h1>
      <p className="text-cocoa-400 mb-6">Track your grade submissions and approval status.</p>

      {isLoading && <div className="flex justify-center py-16"><Spinner className="h-8 w-8" /></div>}
      {error && <ErrorAlert message={getErrorMessage(error)} />}

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-cocoa-50 text-cocoa-500 text-left">
              <tr>
                <th className="px-4 py-3 font-medium">Student ID</th>
                <th className="px-4 py-3 font-medium">Course</th>
                <th className="px-4 py-3 font-medium">Score</th>
                <th className="px-4 py-3 font-medium">Grade</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Submitted</th>
              </tr>
            </thead>
            <tbody>
              {grades?.map((grade) => (
                <tr key={grade.id} className="border-t border-cocoa-50">
                  <td className="px-4 py-3 font-mono text-cocoa-500">{grade.student_id}</td>
                  <td className="px-4 py-3 font-mono text-cocoa-500">{grade.course_id}</td>
                  <td className="px-4 py-3 font-mono">{grade.total_score.toFixed(1)}</td>
                  <td className="px-4 py-3 font-mono font-semibold">{grade.letter_grade}</td>
                  <td className="px-4 py-3"><Badge>{grade.status}</Badge></td>
                  <td className="px-4 py-3">{grade.submitted_date ? new Date(grade.submitted_date).toLocaleString() : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {grades && grades.length === 0 && (
            <CardContent className="text-center text-cocoa-400 py-8">No grade submissions found.</CardContent>
          )}
        </div>
      </Card>
    </AppShell>
  )
}
