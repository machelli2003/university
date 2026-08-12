import { useState } from "react"
import { AppShell } from "@/components/layout/AppShell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Badge, statusToVariant } from "@/components/ui/Badge"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Spinner, ErrorAlert } from "@/components/ui/Feedback"
import { usePendingResults, useApproveResults, useRejectResults } from "@/hooks/useAdmissions"
import { getErrorMessage } from "@/services/api/client"
import type { Applicant } from "@/types/admissions"

export default function PendingResultsPage() {
  const { data: applicants, isLoading, error } = usePendingResults()

  return (
    <AppShell>
      <div className="flex flex-col gap-3 mb-6">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink">Pending Results</h1>
          <p className="text-cocoa-400">Review manually submitted results and approve or reject them.</p>
        </div>
        <div className="flex flex-wrap gap-3">
          <Card className="rounded-2xl border-cocoa-100 bg-brass-50 px-4 py-3">
            <CardContent className="p-0">
              <p className="text-xs uppercase tracking-[0.24em] text-cocoa-500">Pending cases</p>
              <p className="mt-1 text-xl font-semibold text-ink">{applicants?.length ?? 0}</p>
            </CardContent>
          </Card>
          <Card className="rounded-2xl border-cocoa-100 bg-cocoa-50 px-4 py-3">
            <CardContent className="p-0">
              <p className="text-xs uppercase tracking-[0.24em] text-cocoa-500">Next step</p>
              <p className="mt-1 text-sm text-ink">Approve valid results to progress applicants into the admissions pipeline, or reject and return them to resubmit.</p>
            </CardContent>
          </Card>
        </div>
      </div>

      {isLoading && (
        <div className="flex justify-center py-16"><Spinner className="h-8 w-8" /></div>
      )}

      {error && <ErrorAlert message={getErrorMessage(error)} />}

      {applicants && applicants.length === 0 && (
        <Card><CardContent className="py-8 text-center text-cocoa-400">No pending results to review.</CardContent></Card>
      )}

      <div className="space-y-4">
        {applicants?.map((applicant) => (
          <ApplicantResultCard key={applicant.id} applicant={applicant} />
        ))}
      </div>
    </AppShell>
  )
}

function ApplicantResultCard({ applicant }: { applicant: Applicant }) {
  const approveMutation = useApproveResults()
  const rejectMutation = useRejectResults()
  const [rejectReason, setRejectReason] = useState("")
  const [showReject, setShowReject] = useState(false)

  return (
    <Card>
      <CardHeader className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <CardTitle>{applicant.first_name} {applicant.last_name}</CardTitle>
          <p className="text-xs text-cocoa-500">Applicant ID: {applicant.id}</p>
          <p className="text-xs text-cocoa-500">Submitted: {applicant.index_number || "No index"}</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={statusToVariant(applicant.status)}>{applicant.status.replace(/_/g, " ")}</Badge>
        </div>
      </CardHeader>
      <CardContent>
        {(approveMutation.isError || rejectMutation.isError) && (
          <ErrorAlert message={getErrorMessage(approveMutation.error || rejectMutation.error)} />
        )}

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4 text-sm">
          {Object.entries(applicant.results).map(([subject, grade]) => (
            <div key={subject} className="border border-cocoa-100 rounded-md p-3 text-center bg-cocoa-50">
              <p className="text-cocoa-400 text-xs capitalize">{subject.replace(/_/g, " ")}</p>
              <p className="font-mono font-semibold text-lg">{grade}</p>
            </div>
          ))}
        </div>

        <div className="mb-4 text-sm text-cocoa-500">
          <p>Approve this submission to let the applicant proceed to the admissions pipeline.</p>
          <p>If rejected, the applicant will return to the submitted state and must resubmit corrected results.</p>
        </div>

        {!showReject ? (
          <div className="flex flex-wrap gap-3">
            <Button
              onClick={() => approveMutation.mutate({ applicantId: applicant.id })}
              isLoading={approveMutation.isPending}
            >
              Approve results
            </Button>
            <Button variant="outline" onClick={() => setShowReject(true)}>
              Reject results
            </Button>
          </div>
        ) : (
          <div className="space-y-3">
            <Input
              label="Rejection reason"
              placeholder="Enter reason for rejection"
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
            />
            <div className="flex flex-wrap gap-3">
              <Button
                variant="danger"
                isLoading={rejectMutation.isPending}
                onClick={() =>
                  rejectMutation.mutate(
                    { applicantId: applicant.id, reason: rejectReason },
                    { onSuccess: () => setShowReject(false) }
                  )
                }
              >
                Confirm Reject
              </Button>
              <Button variant="ghost" onClick={() => setShowReject(false)}>Cancel</Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
