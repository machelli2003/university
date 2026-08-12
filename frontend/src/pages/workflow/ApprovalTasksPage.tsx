import { AppShell } from "@/components/layout/AppShell"
import { Card, CardContent } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Badge } from "@/components/ui/Badge"
import { Spinner, ErrorAlert } from "@/components/ui/Feedback"
import { useMyApprovalTasks, useProcessApproval } from "@/hooks/useWorkflow"
import { getErrorMessage } from "@/services/api/client"

export default function ApprovalTasksPage() {
  const { data: tasks, isLoading, error } = useMyApprovalTasks()
  const approveMutation = useProcessApproval()

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-semibold text-ink mb-1">My Approval Tasks</h1>
      <p className="text-cocoa-400 mb-6">Workflow steps waiting on your decision.</p>

      {isLoading && <div className="flex justify-center py-16"><Spinner className="h-8 w-8" /></div>}
      {error && <ErrorAlert message={getErrorMessage(error)} />}
      {approveMutation.isError && <ErrorAlert message={getErrorMessage(approveMutation.error)} />}

      <div className="space-y-2">
        {tasks?.map((t) => (
          <Card key={t.id}>
            <CardContent className="flex items-center justify-between py-3">
              <div>
                <p className="text-sm font-medium">Step {t.step_order + 1}</p>
                <Badge>{t.status}</Badge>
              </div>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  isLoading={approveMutation.isPending}
                  onClick={() => approveMutation.mutate({ task_id: t.id, approved: true })}
                >
                  Approve
                </Button>
                <Button
                  size="sm"
                  variant="danger"
                  isLoading={approveMutation.isPending}
                  onClick={() => approveMutation.mutate({ task_id: t.id, approved: false })}
                >
                  Reject
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
        {tasks && tasks.length === 0 && (
          <Card><CardContent className="text-center text-cocoa-400 py-8">No pending approval tasks.</CardContent></Card>
        )}
      </div>
    </AppShell>
  )
}
