import { AppShell } from "@/components/layout/AppShell"
import { Card, CardContent } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Badge } from "@/components/ui/Badge"
import { Spinner, ErrorAlert } from "@/components/ui/Feedback"
import { usePendingGrades, useApproveGrade } from "@/hooks/useExam"
import { getErrorMessage } from "@/services/api/client"

export default function ApproveGradesPage() {
  const { data: grades, isLoading, error } = usePendingGrades()
  const approveMutation = useApproveGrade()

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-semibold text-ink mb-1">Approve Grades</h1>
      <p className="text-cocoa-400 mb-6">Review and approve submitted grades before they're finalized.</p>

      {isLoading && <div className="flex justify-center py-16"><Spinner className="h-8 w-8" /></div>}
      {error && <ErrorAlert message={getErrorMessage(error)} />}
      {approveMutation.isError && <ErrorAlert message={getErrorMessage(approveMutation.error)} />}

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-cocoa-50 text-cocoa-500 text-left">
              <tr>
                <th className="px-4 py-3 font-medium">Student ID</th>
                <th className="px-4 py-3 font-medium">Course ID</th>
                <th className="px-4 py-3 font-medium">Score</th>
                <th className="px-4 py-3 font-medium">Grade</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium"></th>
              </tr>
            </thead>
            <tbody>
              {grades?.map((g) => (
                <tr key={g.id} className="border-t border-cocoa-50">
                  <td className="px-4 py-3 font-mono text-cocoa-500">{g.student_id.slice(0, 10)}...</td>
                  <td className="px-4 py-3 font-mono text-cocoa-500">{g.course_id.slice(0, 10)}...</td>
                  <td className="px-4 py-3 font-mono">{g.total_score.toFixed(1)}</td>
                  <td className="px-4 py-3 font-mono font-semibold">{g.letter_grade}</td>
                  <td className="px-4 py-3"><Badge>{g.status}</Badge></td>
                  <td className="px-4 py-3">
                    <Button
                      size="sm"
                      isLoading={approveMutation.isPending}
                      onClick={() => approveMutation.mutate(g.id)}
                    >
                      Approve
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {grades && grades.length === 0 && (
            <CardContent className="text-center text-cocoa-400 py-8">No grades pending approval.</CardContent>
          )}
        </div>
      </Card>
    </AppShell>
  )
}
