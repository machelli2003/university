/**
 * Application Review & Decision Page
 * Section 39-40: Admissions Officer review workflow
 * 
 * Officer can:
 * - View applicant information
 * - Review submitted documents
 * - Review WASSCE verification status
 * - Check eligibility
 * - Make admission decision (approved/rejected/waitlisted)
 * - Generate admission offer
 */

import React, { useState, useEffect } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { AppShell } from "@/components/layout/AppShell"
import { Button } from "@/components/ui/Button"
import axios from "axios"
import { CheckCircle2, AlertCircle, Clock, FileText, Download, Send } from "lucide-react"

interface ApplicationReview {
  application_id: string
  applicant_id: string
  applicant_name: string
  applicant_email: string
  programme_applied: string
  status: string
  submitted_at: string
  personal_info: any
  academic_info: any
  wassce_status: string
  wassce_verified_at?: string
  verified_by?: string
  eligibility_status: string
  eligibility_notes?: string
  documents: { name: string; url: string; verified: boolean }[]
}

export default function ApplicationReviewPage() {
  const { applicationId } = useParams<{ applicationId: string }>()
  const navigate = useNavigate()
  const [application, setApplication] = useState<ApplicationReview | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [deciding, setDeciding] = useState(false)
  const [decisionNotes, setDecisionNotes] = useState("")
  const [decision, setDecision] = useState<"approve" | "reject" | "waitlist" | null>(null)
  const [showDecisionModal, setShowDecisionModal] = useState(false)

  useEffect(() => {
    loadApplication()
  }, [applicationId])

  async function loadApplication() {
    try {
      setLoading(true)
      const token = localStorage.getItem("access_token")
      const response = await axios.get(`/api/v1/admissions/applications/${applicationId}`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true,
      })
      setApplication(response.data)
    } catch (err: any) {
      setError("Failed to load application")
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  async function handleMakeDecision() {
    if (!application || !decision || !decisionNotes.trim()) return
    setDeciding(true)
    try {
      const token = localStorage.getItem("access_token")
      await axios.post(
        `/api/v1/admissions/applications/${application.application_id}/decision`,
        {
          decision,
          notes: decisionNotes,
        },
        {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true,
        }
      )
      setShowDecisionModal(false)
      await loadApplication()
      setDecision(null)
      setDecisionNotes("")
    } catch (err: any) {
      setError("Failed to record decision")
    } finally {
      setDeciding(false)
    }
  }

  if (loading)
    return (
      <AppShell>
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <Clock className="h-8 w-8 text-cocoa-600 mx-auto mb-2 animate-spin" />
            <p className="text-cocoa-600">Loading application...</p>
          </div>
        </div>
      </AppShell>
    )

  if (error || !application)
    return (
      <AppShell>
        <div className="rounded border border-red-200 bg-red-50 px-4 py-3 text-red-700">{error || "Application not found"}</div>
      </AppShell>
    )

  const statusBgColor =
    application.eligibility_status === "eligible"
      ? "bg-green-50"
      : application.eligibility_status === "ineligible"
        ? "bg-red-50"
        : "bg-yellow-50"

  return (
    <AppShell>
      <div className="max-w-5xl mx-auto space-y-6">
        {/* HEADER */}
        <div className="flex items-start justify-between">
          <div>
            <h1 className="font-display text-3xl font-semibold text-ink">{application.applicant_name}</h1>
            <p className="text-cocoa-600">{application.programme_applied}</p>
          </div>
          <div
            className={`px-4 py-2 rounded-lg font-medium text-sm ${
              application.status === "under_review"
                ? "bg-blue-100 text-blue-800"
                : application.status === "eligible"
                  ? "bg-green-100 text-green-800"
                  : "bg-red-100 text-red-800"
            }`}
          >
            {application.status.replace(/_/g, " ").toUpperCase()}
          </div>
        </div>

        {error && <div className="rounded border border-red-200 bg-red-50 px-4 py-3 text-red-700">{error}</div>}

        <div className="grid gap-6 lg:grid-cols-3">
          {/* LEFT COLUMN: APPLICANT INFO */}
          <div className="lg:col-span-2 space-y-6">
            {/* PERSONAL INFORMATION */}
            <div className="rounded-lg border border-cocoa-100 bg-white p-6">
              <h2 className="font-semibold text-ink mb-4 flex items-center gap-2">
                <FileText className="h-5 w-5" /> Personal Information
              </h2>
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <p className="text-sm font-medium text-cocoa-600">Email</p>
                  <p className="text-ink">{application.applicant_email}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-cocoa-600">Phone</p>
                  <p className="text-ink">{application.personal_info?.phone || "—"}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-cocoa-600">Date of Birth</p>
                  <p className="text-ink">{application.personal_info?.dob || "—"}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-cocoa-600">Gender</p>
                  <p className="text-ink">{application.personal_info?.gender || "—"}</p>
                </div>
              </div>
            </div>

            {/* WASSCE STATUS */}
            <div className={`rounded-lg border border-cocoa-100 p-6 ${statusBgColor}`}>
              <h2 className="font-semibold text-ink mb-4 flex items-center gap-2">
                {application.wassce_status === "verified" ? (
                  <CheckCircle2 className="h-5 w-5 text-green-600" />
                ) : (
                  <AlertCircle className="h-5 w-5 text-yellow-600" />
                )}
                WASSCE Verification
              </h2>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm font-medium text-cocoa-600">Status</span>
                  <span className="text-sm font-bold text-ink uppercase">{application.wassce_status}</span>
                </div>
                {application.wassce_verified_at && (
                  <div className="flex justify-between">
                    <span className="text-sm font-medium text-cocoa-600">Verified By</span>
                    <span className="text-sm text-ink">{application.verified_by || "—"}</span>
                  </div>
                )}
                {application.wassce_verified_at && (
                  <div className="flex justify-between">
                    <span className="text-sm font-medium text-cocoa-600">Verified At</span>
                    <span className="text-sm text-ink">
                      {new Date(application.wassce_verified_at).toLocaleDateString()}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* ELIGIBILITY CHECK */}
            <div className={`rounded-lg border border-cocoa-100 p-6 ${statusBgColor}`}>
              <h2 className="font-semibold text-ink mb-4 flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5" /> Eligibility Status
              </h2>
              <p className="text-sm mb-3">
                <span className="font-bold">{application.eligibility_status.toUpperCase()}</span> for{" "}
                {application.programme_applied}
              </p>
              {application.eligibility_notes && (
                <p className="text-sm text-cocoa-600 bg-white bg-opacity-50 p-3 rounded">{application.eligibility_notes}</p>
              )}
            </div>

            {/* DOCUMENTS */}
            <div className="rounded-lg border border-cocoa-100 bg-white p-6">
              <h2 className="font-semibold text-ink mb-4">📄 Uploaded Documents</h2>
              <div className="space-y-2">
                {application.documents.length > 0 ? (
                  application.documents.map((doc, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 bg-cocoa-50 rounded border border-cocoa-100">
                      <div className="flex items-center gap-3">
                        <FileText className="h-4 w-4 text-cocoa-600" />
                        <span className="text-sm text-ink">{doc.name}</span>
                        {doc.verified && <CheckCircle2 className="h-4 w-4 text-green-600" />}
                      </div>
                      <a href={doc.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                        <Download className="h-4 w-4" />
                      </a>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-cocoa-500">No documents uploaded</p>
                )}
              </div>
            </div>
          </div>

          {/* RIGHT COLUMN: DECISION PANEL */}
          <div className="space-y-4">
            <div className="rounded-lg border border-cocoa-100 bg-white p-6 sticky top-6">
              <h3 className="font-semibold text-ink mb-4">Make Decision</h3>
              <p className="text-sm text-cocoa-600 mb-4">Record your admission decision for this applicant.</p>

              <div className="space-y-2">
                <button
                  onClick={() => {
                    setDecision("approve")
                    setShowDecisionModal(true)
                  }}
                  className="w-full px-4 py-2 rounded-lg bg-green-100 text-green-700 hover:bg-green-200 transition text-sm font-medium border border-green-300"
                >
                  ✅ Approve
                </button>
                <button
                  onClick={() => {
                    setDecision("waitlist")
                    setShowDecisionModal(true)
                  }}
                  className="w-full px-4 py-2 rounded-lg bg-yellow-100 text-yellow-700 hover:bg-yellow-200 transition text-sm font-medium border border-yellow-300"
                >
                  ⏳ Waitlist
                </button>
                <button
                  onClick={() => {
                    setDecision("reject")
                    setShowDecisionModal(true)
                  }}
                  className="w-full px-4 py-2 rounded-lg bg-red-100 text-red-700 hover:bg-red-200 transition text-sm font-medium border border-red-300"
                >
                  ❌ Reject
                </button>
              </div>

              <div className="mt-6 pt-6 border-t border-cocoa-100">
                <Button onClick={() => navigate("/officer/dashboard/admissions")} variant="secondary" className="w-full">
                  Back to Dashboard
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* DECISION MODAL */}
        {showDecisionModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-lg max-w-md p-6">
              <h2 className="text-xl font-bold text-ink mb-4">Record Decision</h2>
              <p className="text-cocoa-600 mb-4">
                Decision: <strong className="text-ink capitalize">{decision}</strong>
              </p>
              <textarea
                value={decisionNotes}
                onChange={(e) => setDecisionNotes(e.target.value)}
                placeholder="Decision notes (required)..."
                className="w-full px-3 py-2 border border-cocoa-200 rounded-md text-sm mb-4 focus:border-cocoa-400"
                rows={4}
              />
              <div className="flex gap-3">
                <Button
                  onClick={handleMakeDecision}
                  disabled={deciding || !decisionNotes.trim()}
                  variant="primary"
                  className="flex-1"
                >
                  {deciding ? "Recording..." : "Record Decision"}
                </Button>
                <Button
                  onClick={() => {
                    setShowDecisionModal(false)
                    setDecision(null)
                    setDecisionNotes("")
                  }}
                  disabled={deciding}
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
