import { AppShell } from "@/components/layout/AppShell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Spinner } from "@/components/ui/Feedback"
import { useAdmissionsSummary, useEnrollmentSummary, useFinanceSummary } from "@/hooks/useAnalytics"
import { formatCurrency } from "@/lib/utils"

function StatCard({ label, value, accent }: { label: string; value: string | number; accent?: string }) {
  return (
    <Card>
      <CardContent className="py-5">
        <p className="text-xs uppercase tracking-wide text-cocoa-400 font-mono mb-1">{label}</p>
        <p className={`text-3xl font-display font-semibold ${accent || "text-ink"}`}>{value}</p>
      </CardContent>
    </Card>
  )
}

export default function AnalyticsDashboardPage() {
  const admissions = useAdmissionsSummary()
  const enrollment = useEnrollmentSummary()
  const finance = useFinanceSummary()

  const isLoading = admissions.isLoading || enrollment.isLoading || finance.isLoading

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-semibold text-ink mb-1">Analytics</h1>
      <p className="text-cocoa-400 mb-6">Live snapshot across admissions, enrollment, and finance.</p>

      {isLoading && <div className="flex justify-center py-16"><Spinner className="h-8 w-8" /></div>}

      {!isLoading && (
        <div className="space-y-8">
          <div>
            <h2 className="text-sm font-medium text-cocoa-500 mb-3">Admissions</h2>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <StatCard label="Total Applications" value={admissions.data?.total_applications ?? 0} />
              <StatCard label="Eligible" value={admissions.data?.eligible ?? 0} accent="text-green-600" />
              <StatCard label="Pending Verification" value={admissions.data?.pending_verification ?? 0} accent="text-brass-500" />
            </div>
          </div>

          <div>
            <h2 className="text-sm font-medium text-cocoa-500 mb-3">Enrollment</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <StatCard label="Active Students" value={enrollment.data?.active_students ?? 0} />
              <StatCard label="On Probation" value={enrollment.data?.on_probation ?? 0} accent="text-red-600" />
            </div>
          </div>

          <div>
            <h2 className="text-sm font-medium text-cocoa-500 mb-3">Finance</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <StatCard
                label="Revenue (30 days)"
                value={formatCurrency(finance.data?.revenue_last_30_days ?? 0)}
                accent="text-green-600"
              />
              <StatCard label="Pending Payments" value={finance.data?.pending_payments ?? 0} accent="text-brass-500" />
            </div>
          </div>
        </div>
      )}
    </AppShell>
  )
}
