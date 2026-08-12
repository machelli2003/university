import { useState } from "react"
import { AppShell } from "@/components/layout/AppShell"
import { Card, CardContent } from "@/components/ui/Card"
import { Badge, statusToVariant } from "@/components/ui/Badge"
import { Select } from "@/components/ui/Select"
import { Spinner, ErrorAlert } from "@/components/ui/Feedback"
import { useAllApplicants } from "@/hooks/useAdmissions"
import { getErrorMessage } from "@/services/api/client"
import { formatDate } from "@/lib/utils"

const STATUS_OPTIONS = [
  "", "draft", "submitted", "awaiting_results", "results_uploaded", "results_approved",
  "eligible", "ineligible", "ranked", "allocated", "offered", "accepted", "rejected",
]

export default function ApplicantsListPage() {
  const [statusFilter, setStatusFilter] = useState("")
  const { data: applicants, isLoading, error } = useAllApplicants(statusFilter || undefined)

  return (
    <AppShell>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink">All Applicants</h1>
          <p className="text-cocoa-400">{applicants?.length ?? 0} total</p>
        </div>
        <Select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="w-56">
          {STATUS_OPTIONS.map((s) => (
            <option key={s} value={s}>{s ? s.replace(/_/g, " ") : "All statuses"}</option>
          ))}
        </Select>
      </div>

      {isLoading && <div className="flex justify-center py-16"><Spinner className="h-8 w-8" /></div>}
      {error && <ErrorAlert message={getErrorMessage(error)} />}

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-cocoa-50 text-cocoa-500 text-left">
              <tr>
                <th className="px-4 py-3 font-medium">Name</th>
                <th className="px-4 py-3 font-medium">Index Number</th>
                <th className="px-4 py-3 font-medium">Aggregate</th>
                <th className="px-4 py-3 font-medium">Merit Rank</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Applied</th>
              </tr>
            </thead>
            <tbody>
              {applicants?.map((a) => (
                <tr key={a.id} className="border-t border-cocoa-50">
                  <td className="px-4 py-3 font-medium"><a href={`/officer/applicants/${a.id}`} className="text-ink hover:underline">{a.first_name} {a.last_name}</a></td>
                  <td className="px-4 py-3 font-mono text-cocoa-500">{a.index_number || "—"}</td>
                  <td className="px-4 py-3 font-mono">{a.aggregate ?? "—"}</td>
                  <td className="px-4 py-3 font-mono">{a.merit_rank ?? "—"}</td>
                  <td className="px-4 py-3">
                    <Badge variant={statusToVariant(a.status)}>{a.status.replace(/_/g, " ")}</Badge>
                  </td>
                  <td className="px-4 py-3 text-cocoa-400">{formatDate(a.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {applicants && applicants.length === 0 && (
            <div className="py-8 text-center text-cocoa-400">No applicants match this filter.</div>
          )}
        </div>
      </Card>
    </AppShell>
  )
}
