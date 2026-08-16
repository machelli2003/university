import { useParams, useNavigate } from "react-router-dom"
import { useEffect, useState } from "react"
import { AppShell } from "@/components/layout/AppShell"
import { Button } from "@/components/ui/Button"
import { onboardingApi, type UniversityApplicationResponse } from "@/services/api/onboarding"
import { getErrorMessage } from "@/services/api/client"
import { Check, Clock, AlertCircle, Play, XCircle } from "lucide-react"

export default function UniversityApplicationDetailPage() {
  const { applicationId } = useParams<{ applicationId: string }>()
  const navigate = useNavigate()
  const [app, setApp] = useState<UniversityApplicationResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [actionLoading, setActionLoading] = useState(false)
  const [showApprovalModal, setShowApprovalModal] = useState(false)
  const [showRejectionModal, setShowRejectionModal] = useState(false)
  const [rejectionReason, setRejectionReason] = useState("")

  useEffect(() => {
    loadApplication()
    const interval = setInterval(loadApplication, 5000) // Refresh every 5s
    return () => clearInterval(interval)
  }, [applicationId])

  async function loadApplication() {
    if (!applicationId) return
    try {
      const data = await onboardingApi.getApplication(applicationId)
      setApp(data)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  async function handleSubmitForReview() {
    if (!app) return
    if (!window.confirm("Submit this application for super admin review? You can edit it later if changes are requested."))
      return

    setActionLoading(true)
    try {
      const updated = await onboardingApi.submitForReview(app.university_application_id)
      setApp(updated)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setActionLoading(false)
    }
  }

  async function handleApprove() {
    if (!app) return
    setActionLoading(true)
    try {
      const updated = await onboardingApi.approveApplication(app.university_application_id)
      setApp(updated)
      setShowApprovalModal(false)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setActionLoading(false)
    }
  }

  async function handleReject() {
    if (!app || !rejectionReason.trim()) return
    setActionLoading(true)
    try {
      const updated = await onboardingApi.rejectApplication(app.university_application_id, rejectionReason)
      setApp(updated)
      setShowRejectionModal(false)
      setRejectionReason("")
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setActionLoading(false)
    }
  }

  async function handleActivate() {
    if (!app) return
    if (!window.confirm("Activate this university? The system will become live and applicants can start applying."))
      return

    setActionLoading(true)
    try {
      const updated = await onboardingApi.activateApplication(app.university_application_id)
      setApp(updated)
      setTimeout(() => {
        navigate("/admin/academic-setup")
      }, 1500)
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
          <p className="text-cocoa-600">Loading application...</p>
        </div>
      </AppShell>
    )

  if (!app)
    return (
      <AppShell>
        <div className="text-center">
          <p className="text-red-600">Application not found</p>
        </div>
      </AppShell>
    )

  const statusConfig: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
    draft: { label: "Draft", color: "bg-gray-100 text-gray-800", icon: <Clock className="h-5 w-5" /> },
    pending_setup: { label: "Pending Setup", color: "bg-blue-100 text-blue-800", icon: <AlertCircle className="h-5 w-5" /> },
    submitted: { label: "Submitted", color: "bg-yellow-100 text-yellow-800", icon: <Clock className="h-5 w-5" /> },
    awaiting_super_admin_approval: {
      label: "Awaiting Approval",
      color: "bg-yellow-100 text-yellow-800",
      icon: <Clock className="h-5 w-5" />,
    },
    approved: { label: "Approved", color: "bg-green-100 text-green-800", icon: <Check className="h-5 w-5" /> },
    provisioning: { label: "Provisioning", color: "bg-blue-100 text-blue-800", icon: <Clock className="h-5 w-5" /> },
    active: { label: "Active", color: "bg-green-100 text-green-800", icon: <Check className="h-5 w-5" /> },
    rejected: { label: "Rejected", color: "bg-red-100 text-red-800", icon: <AlertCircle className="h-5 w-5" /> },
  }

  const status = statusConfig[app.status] || statusConfig.draft

  return (
    <AppShell>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* HEADER */}
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="font-display text-2xl font-semibold text-ink mb-1">{app.legal_name || app.university_information?.legal_name || app.university_application_id}</h1>
            <p className="text-cocoa-600">{app.school_code || app.university_information?.school_code}</p>
          </div>
          <div className={`px-3 py-1 rounded-full flex items-center gap-2 ${status.color} font-medium text-sm`}>
            {status.icon}
            {status.label}
          </div>
        </div>

        {error && <div className="rounded border border-red-200 bg-red-50 px-4 py-3 text-red-700">{error}</div>}

        {/* INFO CARDS */}
        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-lg border border-cocoa-100 p-4 bg-white">
            <h3 className="font-semibold text-ink mb-3">School Details</h3>
            <div className="space-y-2 text-sm text-cocoa-600">
              <div>
                <p className="font-medium text-ink">Legal Name</p>
                <p>{app.legal_name || app.university_information?.legal_name || "—"}</p>
              </div>
              <div>
                <p className="font-medium text-ink">Display Name</p>
                <p>{app.display_name || app.university_information?.display_name || "—"}</p>
              </div>
              <div>
                <p className="font-medium text-ink">School Code</p>
                <p>{app.school_code || app.university_information?.school_code || "—"}</p>
              </div>
              <div>
                <p className="font-medium text-ink">Country</p>
                <p>{app.country || app.university_information?.country || "—"}</p>
              </div>
              <div>
                <p className="font-medium text-ink">Timezone</p>
                <p>{app.timezone || app.university_information?.timezone || "—"}</p>
              </div>
            </div>
          </div>

          <div className="rounded-lg border border-cocoa-100 p-4 bg-white">
            <h3 className="font-semibold text-ink mb-3">Administrator</h3>
            <div className="space-y-2 text-sm text-cocoa-600">
              <div>
                <p className="font-medium text-ink">Name</p>
                <p>
                  {app.admin_first_name} {app.admin_last_name}
                </p>
              </div>
              <div>
                <p className="font-medium text-ink">Email</p>
                <p>{app.admin_email}</p>
              </div>
              <div>
                <p className="font-medium text-ink">Official Email</p>
                <p>{app.official_email || "—"}</p>
              </div>
              <div>
                <p className="font-medium text-ink">Official Phone</p>
                <p>{app.official_phone || "—"}</p>
              </div>
            </div>
          </div>
        </div>

        {/* SETUP PROGRESS */}
        {app.setup_sections && (
          <div className="rounded-lg border border-cocoa-100 p-4 bg-white">
            <h3 className="font-semibold text-ink mb-4">Setup Progress</h3>
            <div className="grid gap-2 max-w-2xl">
              {Object.entries(app.setup_sections).map(([section, completed]) => (
                <div key={section} className="flex items-center gap-3">
                  <div
                    className={`h-5 w-5 rounded border-2 flex items-center justify-center ${
                      completed ? "border-green-600 bg-green-600" : "border-cocoa-200"
                    }`}
                  >
                    {completed && <Check className="h-3 w-3 text-white" />}
                  </div>
                  <span className="text-sm capitalize text-cocoa-600">{section.replace(/_/g, " ")}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TIMELINE */}
        <div className="rounded-lg border border-cocoa-100 p-4 bg-white">
          <h3 className="font-semibold text-ink mb-4">Timeline</h3>
          <div className="space-y-2 text-sm text-cocoa-600">
            {app.submitted_at && (
              <div>
                <p className="font-medium text-ink">Submitted for Review</p>
                <p>{new Date(app.submitted_at).toLocaleString()}</p>
              </div>
            )}
            {app.approved_at && (
              <div>
                <p className="font-medium text-ink">Approved by Super Admin</p>
                <p>{new Date(app.approved_at).toLocaleString()}</p>
              </div>
            )}
            {app.activated_at && (
              <div>
                <p className="font-medium text-ink">Activated</p>
                <p>{new Date(app.activated_at).toLocaleString()}</p>
              </div>
            )}
          </div>
        </div>

        {/* ACTION BUTTONS */}
        <div className="flex flex-wrap gap-3">
          {app.status === "draft" && (
            <Button onClick={handleSubmitForReview} disabled={actionLoading} variant="primary">
              Submit for Review
            </Button>
          )}

          {app.status === "awaiting_super_admin_approval" && (
            <>
              <Button
                onClick={() => setShowApprovalModal(true)}
                disabled={actionLoading}
                variant="primary"
                className="bg-green-600 hover:bg-green-700"
              >
                <Check className="h-4 w-4 mr-2" /> Approve
              </Button>
              <Button
                onClick={() => setShowRejectionModal(true)}
                disabled={actionLoading}
                variant="secondary"
                className="bg-red-100 text-red-700 hover:bg-red-200 border border-red-300"
              >
                <XCircle className="h-4 w-4 mr-2" /> Reject
              </Button>
            </>
          )}

          {(app.status === "approved" || app.status === "provisioning") && (
            <Button
              onClick={handleActivate}
              disabled={actionLoading}
              variant="primary"
              className="flex items-center gap-2"
            >
              <Play className="h-4 w-4" /> Activate University
            </Button>
          )}

          {app.status === "active" && (
            <Button onClick={() => navigate("/admin/academic-setup")} variant="primary">
              Go to Academic Setup
            </Button>
          )}

          <Button onClick={() => navigate("/admin/university-applications")} variant="secondary">
            Back to Applications
          </Button>
        </div>

        {/* APPROVAL MODAL */}
        {showApprovalModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-lg max-w-md p-6">
              <h2 className="text-xl font-bold text-ink mb-4">Approve University Application?</h2>
              <p className="text-cocoa-600 mb-6">
                This will approve the setup for <strong>{app.legal_name}</strong>. The university admin can then activate it to make it live.
              </p>
              <div className="flex gap-3">
                <Button
                  onClick={handleApprove}
                  disabled={actionLoading}
                  variant="primary"
                  className="flex-1 bg-green-600"
                >
                  {actionLoading ? "Approving..." : "Approve"}
                </Button>
                <Button
                  onClick={() => setShowApprovalModal(false)}
                  disabled={actionLoading}
                  variant="secondary"
                  className="flex-1"
                >
                  Cancel
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* REJECTION MODAL */}
        {showRejectionModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-lg max-w-md p-6">
              <h2 className="text-xl font-bold text-ink mb-4">Reject Application</h2>
              <p className="text-cocoa-600 mb-4">
                Provide a reason for rejecting this university setup application.
              </p>
              <textarea
                value={rejectionReason}
                onChange={(e) => setRejectionReason(e.target.value)}
                placeholder="Reason for rejection..."
                className="w-full px-3 py-2 border border-cocoa-200 rounded-md text-sm mb-4"
                rows={4}
              />
              <div className="flex gap-3">
                <Button
                  onClick={handleReject}
                  disabled={actionLoading || !rejectionReason.trim()}
                  variant="primary"
                  className="flex-1 bg-red-600"
                >
                  {actionLoading ? "Rejecting..." : "Reject"}
                </Button>
                <Button
                  onClick={() => {
                    setShowRejectionModal(false)
                    setRejectionReason("")
                  }}
                  disabled={actionLoading}
                  variant="secondary"
                  className="flex-1"
                >
                  Cancel
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  )
}
