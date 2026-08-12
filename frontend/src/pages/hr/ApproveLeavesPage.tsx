import { AppShell } from "@/components/layout/AppShell"
import { Card, CardContent } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Spinner, ErrorAlert } from "@/components/ui/Feedback"
import { usePendingLeaves, useApproveLeave, useRejectLeave } from "@/hooks/useHr"
import { getErrorMessage } from "@/services/api/client"

export default function ApproveLeavesPage() {
  const { data: leaves, isLoading, error } = usePendingLeaves()
  const approveMutation = useApproveLeave()
  const rejectMutation = useRejectLeave()

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-semibold text-ink mb-1">Approve Leave Requests</h1>
      <p className="text-cocoa-400 mb-6">Review pending staff leave applications.</p>

      {isLoading && <div className="flex justify-center py-16"><Spinner className="h-8 w-8" /></div>}
      {error && <ErrorAlert message={getErrorMessage(error)} />}
      {(approveMutation.isError || rejectMutation.isError) && (
        <ErrorAlert message={getErrorMessage(approveMutation.error || rejectMutation.error)} />
      )}

      <div className="space-y-3">
        {leaves?.map((leave) => (
          <Card key={leave.id}>
            <CardContent className="flex items-center justify-between py-4">
              <div>
                <p className="font-medium text-sm capitalize">{leave.leave_type} leave</p>
                <p className="text-xs text-cocoa-400">{leave.reason}</p>
                <p className="text-xs text-cocoa-300 font-mono mt-1">Staff: {leave.staff_id.slice(0, 10)}...</p>
              </div>
              <div className="flex gap-2">
                <Button size="sm" isLoading={approveMutation.isPending} onClick={() => approveMutation.mutate(leave.id)}>
                  Approve
                </Button>
                <Button size="sm" variant="danger" isLoading={rejectMutation.isPending} onClick={() => rejectMutation.mutate(leave.id)}>
                  Reject
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
        {leaves && leaves.length === 0 && (
          <Card><CardContent className="text-center text-cocoa-400 py-8">No pending leave requests.</CardContent></Card>
        )}
      </div>
    </AppShell>
  )
}
