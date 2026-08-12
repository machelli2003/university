import { useState } from "react"
import { AppShell } from "@/components/layout/AppShell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Select } from "@/components/ui/Select"
import { ErrorAlert, SuccessAlert } from "@/components/ui/Feedback"
import {
  useBulkEvaluateEligibility,
  useAllocateProgrammes,
  usePublishOffers,
  useProcessAdmissions,
  useProgrammes,
} from "@/hooks/useAdmissions"
import { useMutation } from "@tanstack/react-query"
import { admissionsApi } from "@/services/api/admissions"
import { getErrorMessage } from "@/services/api/client"
import type { RankingResultItem } from "@/types/admissions"

export default function ProcessingPage() {
  return (
    <AppShell>
      <h1 className="font-display text-2xl font-semibold text-ink mb-1">Process Admissions</h1>
      <p className="text-cocoa-400 mb-6">
        Run the admissions pipeline: eligibility → ranking → allocation → offers.
      </p>

      <div className="space-y-6">
        <EligibilityStep />
        <RankingStep />
        <AllocationStep />
        <PublishStep />
        <ProcessPipelineStep />
      </div>
    </AppShell>
  )
}

function ProcessPipelineStep() {
  const mutation = useProcessAdmissions()

  return (
    <StepCard
      step={5}
      title="Run Full Pipeline"
      description="Execute eligibility, ranking, allocation, and offer publishing in one action."
    >
      {mutation.isError && <ErrorAlert message={getErrorMessage(mutation.error)} />}
      {mutation.isSuccess && (
        <SuccessAlert
          message={`Eligible: ${mutation.data.eligible}, Ranked: ${mutation.data.ranked}, Allocated: ${mutation.data.allocated}, Published: ${mutation.data.offers_published}`}
        />
      )}
      <Button onClick={() => mutation.mutate()} isLoading={mutation.isPending}>
        Run Full Pipeline
      </Button>
    </StepCard>
  )
}

function StepCard({
  step,
  title,
  description,
  children,
}: {
  step: number
  title: string
  description: string
  children: React.ReactNode
}) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-3">
          <span className="flex h-7 w-7 items-center justify-center rounded-full bg-cocoa-600 text-white text-sm font-mono">
            {step}
          </span>
          <CardTitle>{title}</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-cocoa-500 mb-4">{description}</p>
        {children}
      </CardContent>
    </Card>
  )
}

function EligibilityStep() {
  const mutation = useBulkEvaluateEligibility()

  return (
    <StepCard
      step={1}
      title="Evaluate Eligibility"
      description="Check all applicants with approved results against their chosen programme requirements."
    >
      {mutation.isError && <ErrorAlert message={getErrorMessage(mutation.error)} />}
      {mutation.isSuccess && (
        <SuccessAlert
          message={`Processed: ${mutation.data.eligible ?? 0} eligible, ${mutation.data.ineligible ?? 0} ineligible.`}
        />
      )}
      <Button onClick={() => mutation.mutate()} isLoading={mutation.isPending}>
        Run Eligibility Check
      </Button>
    </StepCard>
  )
}

function RankingStep() {
  const { data: programmes } = useProgrammes()
  const [programmeId, setProgrammeId] = useState("")

  const rankMutation = useMutation({
    mutationFn: (id: string) => admissionsApi.rankApplicants(id),
  })

  return (
    <StepCard
      step={2}
      title="Rank Applicants"
      description="Calculate merit scores and rank eligible applicants for a specific programme."
    >
      {rankMutation.isError && <ErrorAlert message={getErrorMessage(rankMutation.error)} />}

      <div className="flex gap-3 mb-4">
        <Select value={programmeId} onChange={(e) => setProgrammeId(e.target.value)} className="max-w-xs">
          <option value="">Select programme...</option>
          {programmes?.map((p) => (
            <option key={p.id} value={p.id}>{p.name}</option>
          ))}
        </Select>
        <Button
          disabled={!programmeId}
          isLoading={rankMutation.isPending}
          onClick={() => rankMutation.mutate(programmeId)}
        >
          Rank
        </Button>
      </div>

      {rankMutation.data && rankMutation.data.length > 0 && (
        <RankingTable results={rankMutation.data} />
      )}
    </StepCard>
  )
}

function RankingTable({ results }: { results: RankingResultItem[] }) {
  return (
    <div className="overflow-x-auto border border-cocoa-100 rounded-md">
      <table className="w-full text-sm">
        <thead className="bg-cocoa-50 text-cocoa-500 text-left">
          <tr>
            <th className="px-3 py-2 font-medium">Rank</th>
            <th className="px-3 py-2 font-medium">Applicant ID</th>
            <th className="px-3 py-2 font-medium">Merit Score</th>
            <th className="px-3 py-2 font-medium">Aggregate</th>
          </tr>
        </thead>
        <tbody>
          {results.map((r) => (
            <tr key={r.applicant_id} className="border-t border-cocoa-50">
              <td className="px-3 py-2 font-mono">{r.merit_rank}</td>
              <td className="px-3 py-2 font-mono text-cocoa-500">{r.applicant_id.slice(0, 10)}...</td>
              <td className="px-3 py-2 font-mono">{r.merit_score.toFixed(1)}</td>
              <td className="px-3 py-2 font-mono">{r.aggregate ?? "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function AllocationStep() {
  const mutation = useAllocateProgrammes()

  return (
    <StepCard
      step={3}
      title="Allocate Programmes"
      description="Assign ranked applicants to programmes based on capacity and choice order."
    >
      {mutation.isError && <ErrorAlert message={getErrorMessage(mutation.error)} />}
      {mutation.isSuccess && (
        <SuccessAlert
          message={`Processed ${mutation.data.total_processed}: ${mutation.data.allocated} allocated, ${mutation.data.waitlisted} waitlisted.`}
        />
      )}
      <Button onClick={() => mutation.mutate()} isLoading={mutation.isPending}>
        Run Allocation
      </Button>
    </StepCard>
  )
}

function PublishStep() {
  const mutation = usePublishOffers()

  return (
    <StepCard
      step={4}
      title="Publish Offers"
      description="Send admission offers to all allocated applicants."
    >
      {mutation.isError && <ErrorAlert message={getErrorMessage(mutation.error)} />}
      {mutation.isSuccess && (
        <SuccessAlert message={`Published ${mutation.data.published_offers} offers.`} />
      )}
      <Button onClick={() => mutation.mutate()} isLoading={mutation.isPending}>
        Publish Offers
      </Button>
    </StepCard>
  )
}
