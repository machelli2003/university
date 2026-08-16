import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { AppShell } from "@/components/layout/AppShell"
import { onboardingApi, type UniversityApplicationResponse } from "@/services/api/onboarding"
import { useAuthStore } from "@/store/authStore"
import { getErrorMessage } from "@/services/api/client"
import { Plus, ChevronRight } from "lucide-react"

export default function UniversityApplicationsPage() {
  const navigate = useNavigate()
  const user = useAuthStore((s) => s.user)
  const [applications, setApplications] = useState<UniversityApplicationResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadApplications()
  }, [])

  async function loadApplications() {
    try {
      const data = await onboardingApi.listApplications()
      setApplications(data)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  const statusConfig: Record<string, { label: string; color: string }> = {
    draft: { label: "Draft", color: "bg-gray-100 text-gray-800" },
    pending_setup: { label: "Pending Setup", color: "bg-blue-100 text-blue-800" },
    submitted: { label: "Submitted", color: "bg-yellow-100 text-yellow-800" },
    awaiting_super_admin_approval: { label: "Awaiting Approval", color: "bg-yellow-100 text-yellow-800" },
    approved: { label: "Approved", color: "bg-green-100 text-green-800" },
    provisioning: { label: "Provisioning", color: "bg-blue-100 text-blue-800" },
    active: { label: "Active", color: "bg-green-100 text-green-800" },
    rejected: { label: "Rejected", color: "bg-red-100 text-red-800" },
  }

  if (loading)
    return (
      <AppShell>
        <div className="flex items-center justify-center h-64">
          <p className="text-cocoa-600">Loading applications...</p>
        </div>
      </AppShell>
    )

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-display text-2xl font-semibold text-ink mb-1">University Applications</h1>
            <p className="text-cocoa-400">
              {user?.role === "super_admin"
                ? "Review and manage all university applications"
                : "View and manage your university applications"}
            </p>
          </div>
          {user?.role === "super_admin" && (
            <button
              onClick={() => navigate("/admin/university-application/new")}
              className="btn btn-primary flex items-center gap-2"
            >
              <Plus className="h-4 w-4" /> New Application
            </button>
          )}
        </div>

        {error && <div className="rounded border border-red-200 bg-red-50 px-4 py-3 text-red-700">{error}</div>}

        {applications.length === 0 ? (
          <div className="rounded-lg border border-cocoa-100 bg-white p-8 text-center">
            <p className="text-cocoa-600 mb-4">No applications yet.</p>
            {user?.role === "super_admin" && (
              <button
                onClick={() => navigate("/admin/university-application/new")}
                className="btn btn-primary inline-flex items-center gap-2"
              >
                <Plus className="h-4 w-4" /> Create First Application
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-3">
            {applications.map((app) => {
              const status = statusConfig[app.status] || statusConfig.draft
              return (
                <div
                  key={app.id}
                  onClick={() => navigate(`/admin/university-applications/${app.university_application_id}`)}
                  className="rounded-lg border border-cocoa-100 p-4 bg-white hover:border-cocoa-200 hover:bg-cocoa-50 cursor-pointer transition"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <h3 className="font-semibold text-ink">{app.legal_name}</h3>
                      <p className="text-sm text-cocoa-600 mt-1">
                        {app.school_code} • {app.admin_first_name} {app.admin_last_name}
                      </p>
                      <p className="text-sm text-cocoa-500 mt-2">
                        {Object.values(app.setup_sections).filter(Boolean).length} of{" "}
                        {Object.keys(app.setup_sections).length} sections complete
                      </p>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${status.color}`}>{status.label}</span>
                      <ChevronRight className="h-5 w-5 text-cocoa-400" />
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </AppShell>
  )
}
