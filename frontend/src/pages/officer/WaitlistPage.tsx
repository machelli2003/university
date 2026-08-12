import { useState } from "react"
import { AppShell } from "@/components/layout/AppShell"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card"
import { Select } from "@/components/ui/Select"
import { Button } from "@/components/ui/Button"
import { useWaitlist, useProgrammes, usePromoteWaitlist } from "@/hooks/useAdmissions"

export default function WaitlistPage() {
  const [programme, setProgramme] = useState<string>("")
  const programmesQuery = useProgrammes()
  const waitlistQuery = useWaitlist(programme || undefined)
  const promoteMutation = usePromoteWaitlist()
  const [promoteCount, setPromoteCount] = useState<number>(1)
  const isPromotePending = promoteMutation.status === "pending"

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink">Waitlist Management</h1>
          <p className="text-cocoa-400">View and promote waitlisted applicants for programmes.</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Filters</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-3">
              <Select value={programme} onChange={(e) => setProgramme(e.target.value)}>
                <option value="">All programmes</option>
                {programmesQuery.data?.map((p) => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </Select>

              <div>
                <label className="block text-sm text-cocoa-600">Promote count</label>
                <input type="number" value={promoteCount} onChange={(e) => setPromoteCount(Math.max(1, parseInt(e.target.value || "1")))} className="rounded border px-2 py-1" />
              </div>

              <div>
                <Button onClick={() => promoteMutation.mutate({ programme_id: programme, count: promoteCount })} isLoading={isPromotePending}>Promote</Button>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Waitlisted Applicants</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {waitlistQuery.data?.map((w) => (
                <div key={w.id} className="rounded-lg border border-cocoa-100 p-3">
                  <div className="flex justify-between">
                    <div>
                      <p className="font-semibold">{w.first_name} {w.last_name}</p>
                      <p className="text-sm text-cocoa-500">Merit rank: {w.merit_rank ?? "—"}</p>
                    </div>
                  </div>
                </div>
              ))}
              {waitlistQuery.data && waitlistQuery.data.length === 0 && (
                <p className="text-sm text-cocoa-400">No waitlisted applicants found.</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  )
}
