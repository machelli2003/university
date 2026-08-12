import { AppShell } from "@/components/layout/AppShell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { ProposalApprovalPanel } from "@/components/research/ProposalApprovalPanel"

export default function DeanPage() {
  return (
    <AppShell>
      <h1 className="font-display text-2xl font-semibold text-ink mb-1">Dean Dashboard</h1>
      <p className="text-cocoa-400 mb-6">Provide college-level oversight for academic programmes, policy approval, and faculty performance.</p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <Card>
          <CardHeader>
            <CardTitle>Academic Oversight</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-cocoa-500">Review curriculum proposals, monitor departmental standards, and guide academic strategy.</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Approval Routing</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-cocoa-500">Approve grade workflows, policy changes, and departmental requests at the faculty level.</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Research & Grants</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-cocoa-500">Support faculty research initiatives, grant approvals, and publication tracking.</p>
          </CardContent>
        </Card>
      </div>

      <ProposalApprovalPanel />
    </AppShell>
  )
}
