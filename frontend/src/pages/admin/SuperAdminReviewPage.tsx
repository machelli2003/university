import { useState, useEffect } from "react"
import { AppShell } from "@/components/layout/AppShell"
import { onboardingApi, type UniversityApplicationResponse } from "@/services/api/onboarding"
import { getErrorMessage } from "@/services/api/client"
import { Check, X, ChevronRight } from "lucide-react"

export default function SuperAdminReviewPage() {
  const [applications, setApplications] = useState<UniversityApplicationResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedApp, setSelectedApp] = useState<UniversityApplicationResponse | null>(null)
  const [rejectReason, setRejectReason] = useState("")
  const [actionLoading, setActionLoading] = useState(false)

  useEffect(() => {
    loadPendingApplications()
  }, [])

  async function loadPendingApplications() {
    try {
      setLoading(true)
      const data = await onboardingApi.listApplications("awaiting_super_admin_approval")
      setApplications(data)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  async function handleApprove(app: UniversityApplicationResponse) {
    if (!window.confirm(`Approve ${app.legal_name}? The university setup will be created and ready for activation.`))
      return

    setActionLoading(true)
    try {
      await onboardingApi.approveApplication(app.university_application_id)
      setSelectedApp(null)
      await loadPendingApplications()
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setActionLoading(false)
    }
  }

  async function handleReject(app: UniversityApplicationResponse) {
    if (!rejectReason.trim()) {
      alert("Please provide a reason for rejection")
      return
    }

    if (!window.confirm(`Reject ${app.legal_name}?`)) return

    setActionLoading(true)
    try {
      await onboardingApi.rejectApplication(app.university_application_id, rejectReason)
      setSelectedApp(null)
      setRejectReason("")
      await loadPendingApplications()
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setActionLoading(false)
    }
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
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink mb-1">University Applications Review</h1>
          <p className="text-cocoa-400 mb-6">Review and approve pending university applications from administrators.</p>
        </div>

        {error && <div className="rounded border border-red-200 bg-red-50 px-4 py-3 text-red-700">{error}</div>}

        {applications.length === 0 ? (
          <div className="rounded-lg border border-cocoa-100 bg-white p-8 text-center">
            <p className="text-cocoa-600">No pending applications to review.</p>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {applications.map((app) => (
              <div
                key={app.id}
                className="rounded-lg border border-cocoa-100 p-4 bg-white hover:border-cocoa-200 cursor-pointer transition"
                onClick={() => setSelectedApp(app)}
              >
                <div className="mb-3">
                  <h3 className="font-semibold text-ink">{app.legal_name}</h3>
                  <p className="text-sm text-cocoa-600">{app.school_code}</p>
                </div>
                <div className="space-y-1 text-sm text-cocoa-600 mb-4">
                  <p>Admin: {app.admin_first_name} {app.admin_last_name}</p>
                  <p className="truncate">{app.admin_email}</p>
                </div>
                <div className="flex items-center gap-2 text-cocoa-500 font-medium">
                  View Details <ChevronRight className="h-4 w-4" />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* MODAL FOR APPLICATION DETAILS */}
      {selectedApp && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-cocoa-100 p-6">
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-ink">{selectedApp.legal_name}</h2>
                  <p className="text-sm text-cocoa-600">{selectedApp.school_code}</p>
                </div>
                <button
                  onClick={() => {
                    setSelectedApp(null)
                    setRejectReason("")
                  }}
                  className="text-cocoa-500 hover:text-ink"
                >
                  ✕
                </button>
              </div>
            </div>

            <div className="p-6 space-y-6">
              {/* School Info */}
              <div className="space-y-3">
                <h3 className="font-semibold text-ink">School Information</h3>
                <div className="grid gap-3 text-sm">
                  <div>
                    <p className="text-cocoa-600">Legal Name</p>
                    <p className="font-medium text-ink">{selectedApp.university_information?.legal_name || "—"}</p>
                  </div>
                  <div>
                    <p className="text-cocoa-600">Display Name</p>
                    <p className="font-medium text-ink">{selectedApp.university_information?.display_name || "—"}</p>
                  </div>
                  <div>
                    <p className="text-cocoa-600">Country</p>
                    <p className="font-medium text-ink">{selectedApp.university_information?.country || "—"}</p>
                  </div>
                  <div>
                    <p className="text-cocoa-600">Timezone</p>
                    <p className="font-medium text-ink">{selectedApp.university_information?.timezone || "—"}</p>
                  </div>
                </div>
              </div>

              {/* Admin Info */}
              <div className="space-y-3">
                <h3 className="font-semibold text-ink">Administrator Contact</h3>
                <div className="grid gap-3 text-sm">
                  <div>
                    <p className="text-cocoa-600">Name</p>
                    <p className="font-medium text-ink">
                      {selectedApp.admin_first_name} {selectedApp.admin_last_name}
                    </p>
                  </div>
                  <div>
                    <p className="text-cocoa-600">Email</p>
                    <p className="font-medium text-ink">{selectedApp.admin_email}</p>
                  </div>
                  <div>
                    <p className="text-cocoa-600">Official Email</p>
                    <p className="font-medium text-ink">{selectedApp.official_email || "—"}</p>
                  </div>
                  <div>
                    <p className="text-cocoa-600">Official Phone</p>
                    <p className="font-medium text-ink">{selectedApp.official_phone || "—"}</p>
                  </div>
                </div>
              </div>

              {/* Setup Status */}
              {selectedApp.setup_sections && (
                <div className="space-y-3">
                  <h3 className="font-semibold text-ink">Setup Progress</h3>
                  <div className="grid gap-2 text-sm">
                    {Object.entries(selectedApp.setup_sections).map(([section, completed]) => (
                      <div key={section} className="flex items-center gap-2">
                        {completed ? (
                          <Check className="h-4 w-4 text-green-600" />
                        ) : (
                          <div className="h-4 w-4 rounded border border-cocoa-200" />
                        )}
                        <span className="capitalize text-cocoa-600">{section.replace(/_/g, " ")}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Rejection Reason (if rejecting) */}
              <div className="space-y-3">
                <h3 className="font-semibold text-ink">Decision</h3>
                <textarea
                  className="w-full input min-h-[100px]"
                  placeholder="Add feedback or reason for rejection (required if rejecting)..."
                  value={rejectReason}
                  onChange={(e) => setRejectReason(e.target.value)}
                />
              </div>
            </div>

            {/* Actions */}
            <div className="sticky bottom-0 bg-white border-t border-cocoa-100 p-6 flex gap-3 justify-end">
              <button
                onClick={() => {
                  setSelectedApp(null)
                  setRejectReason("")
                }}
                className="btn btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={() => handleReject(selectedApp)}
                disabled={actionLoading}
                className="btn btn-danger flex items-center gap-2"
              >
                <X className="h-4 w-4" /> Reject
              </button>
              <button
                onClick={() => handleApprove(selectedApp)}
                disabled={actionLoading}
                className="btn btn-primary flex items-center gap-2"
              >
                <Check className="h-4 w-4" /> Approve & Provision
              </button>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  )
}
