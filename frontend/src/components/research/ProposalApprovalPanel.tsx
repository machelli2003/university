import { useState } from "react"
import { Button } from "@/components/ui/Button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { ErrorAlert, Spinner, SuccessAlert } from "@/components/ui/Feedback"
import { usePendingProposals, useApproveProposal } from "@/hooks/useResearch"
import type { ProposalItem } from "@/types/research"

export function ProposalApprovalPanel() {
  const pendingProposalsQuery = usePendingProposals()
  const approveProposalMutation = useApproveProposal()
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  async function handleApprove(proposalId: string) {
    setSuccessMessage(null)
    try {
      await approveProposalMutation.mutateAsync(proposalId)
      setSuccessMessage("Research proposal approved.")
    } catch (error) {
      // error state handled by mutation
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Research Proposal Approval</CardTitle>
      </CardHeader>
      <CardContent>
        {pendingProposalsQuery.isError && (
          <ErrorAlert message={pendingProposalsQuery.error instanceof Error ? pendingProposalsQuery.error.message : "Failed to load proposals."} />
        )}

        {approveProposalMutation.isError && (
          <ErrorAlert message={approveProposalMutation.error instanceof Error ? approveProposalMutation.error.message : "Failed to approve proposal."} />
        )}

        {successMessage && <SuccessAlert message={successMessage} />}

        {pendingProposalsQuery.isLoading ? (
          <div className="py-10 text-center">
            <Spinner />
          </div>
        ) : (
          <div className="space-y-3">
            {pendingProposalsQuery.data?.length ? (
              pendingProposalsQuery.data.map((proposal: ProposalItem) => (
                <div key={proposal.id} className="grid grid-cols-1 md:grid-cols-4 gap-3 items-center rounded border border-cocoa-100 p-4">
                  <div className="md:col-span-2">
                    <p className="font-medium">{proposal.title}</p>
                    <p className="text-xs text-cocoa-400">Submitted by {proposal.researcher_id}</p>
                  </div>
                  <div className="text-sm text-cocoa-500">Pending approval</div>
                  <Button
                    size="sm"
                    onClick={() => handleApprove(proposal.id)}
                    isLoading={approveProposalMutation.isPending}
                    disabled={approveProposalMutation.isPending}
                  >
                    Approve
                  </Button>
                </div>
              ))
            ) : (
              <p className="text-sm text-cocoa-500">No research proposals awaiting approval.</p>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
