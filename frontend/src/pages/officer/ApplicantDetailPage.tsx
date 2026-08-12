import { useState } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { AppShell } from "@/components/layout/AppShell"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card"
import { Input } from "@/components/ui/Input"
import { Button } from "@/components/ui/Button"
import { useMyApplication, useOverrideApplicant, useReopenApplication, useNotifyOffer, useProgrammes, useProgrammeCapacity } from "@/hooks/useAdmissions"
import { Spinner } from "@/components/ui/Feedback"

export default function ApplicantDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { data: applicant, isLoading } = useMyApplication(id)
  const overrideMutation = useOverrideApplicant(id || "")
  const reopenMutation = useReopenApplication(id || "")
  const notifyMutation = useNotifyOffer(id || "")
  const programmesQuery = useProgrammes()
  const [meritScore, setMeritScore] = useState<string>("")
  const [isEligible, setIsEligible] = useState<string>("")

  const programmeCapacityQuery = useProgrammeCapacity(applicant?.allocated_programme_id || "")
  const isOverridePending = overrideMutation.status === "pending"
  const isReopenPending = reopenMutation.status === "pending"
  const isNotifyPending = notifyMutation.status === "pending"

  if (isLoading) return <AppShell><div className="py-16 flex justify-center"><Spinner className="h-8 w-8" /></div></AppShell>
  if (!applicant) return <AppShell><div className="py-16 text-center">Applicant not found</div></AppShell>

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-display text-2xl font-semibold text-ink">{applicant.first_name} {applicant.last_name}</h1>
            <p className="text-cocoa-500">Status: {applicant.status}</p>
          </div>
          <div>
            <Button variant="secondary" onClick={() => navigate(-1)}>Back</Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Contact</CardTitle>
            </CardHeader>
            <CardContent>
              <p>{applicant.phone}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Academic</CardTitle>
            </CardHeader>
            <CardContent>
              <p>Index: {applicant.index_number || "—"}</p>
              <p>Aggregate: {applicant.aggregate ?? "—"}</p>
              <p>Merit score: {applicant.merit_score ?? "—"}</p>
              <p>Merit rank: {applicant.merit_rank ?? "—"}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Programme</CardTitle>
            </CardHeader>
            <CardContent>
              <p>Allocated: {applicant.allocated_programme_id || "—"}</p>
              {programmeCapacityQuery.data && (
                <p>Capacity available: {programmeCapacityQuery.data.available}</p>
              )}
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div>
                <label className="block text-sm text-cocoa-600">Merit score</label>
                <Input value={meritScore} onChange={(e) => setMeritScore(e.target.value)} placeholder="e.g. 12.5" />
                <label className="block text-sm text-cocoa-600 mt-2">Is eligible</label>
                <select value={isEligible} onChange={(e) => setIsEligible(e.target.value)} className="mt-1 block w-full rounded border">
                  <option value="">No change</option>
                  <option value="true">Eligible</option>
                  <option value="false">Ineligible</option>
                </select>
                <div className="mt-3">
                  <Button onClick={() => overrideMutation.mutate({ merit_score: meritScore ? parseFloat(meritScore) : undefined, is_eligible: isEligible === "true" ? true : (isEligible === "false" ? false : undefined) })} isLoading={isOverridePending}>Apply Override</Button>
                </div>
              </div>

              <div>
                <p className="text-sm text-cocoa-500">Reopen application if rejected or closed.</p>
                <div className="mt-3">
                  <Button variant="secondary" onClick={() => reopenMutation.mutate() } isLoading={isReopenPending}>Reopen Application</Button>
                </div>
              </div>

              <div>
                <p className="text-sm text-cocoa-500">Notify applicant of offer (email/SMS)</p>
                <div className="mt-3">
                  <Button variant="ghost" onClick={() => notifyMutation.mutate()} isLoading={isNotifyPending}>Send Offer Notification</Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Programme Choices & Timeline</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="text-xs bg-surface p-3 rounded">{JSON.stringify({ choices: applicant.programme_choices, results: applicant.results }, null, 2)}</pre>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  )
}
