/**
 * Admissions Officer WASSCE Verification Page
 * Section 37: WASSCE Verification UI
 * 
 * Officer reviews:
 * - Applicant information
 * - Submitted WASSCE results
 * - Uploaded evidence
 * 
 * Officer can:
 * - Verify results
 * - Reject results
 * - Request corrections
 * - Record verification notes
 */

import React, { useState, useEffect } from "react"
import { Button } from "@/components/ui/Button"
import axios from "axios"

interface PendingApplicant {
  applicant_id: string
  first_name: string
  last_name: string
  email: string
  index_number: string
  exam_year: number
  submitted_at: string
  verification_status: string
}

export default function OfficerWASSCEVerificationPage() {
  const [pendingApplicants, setPendingApplicants] = useState<PendingApplicant[]>([])
  const [selectedApplicant, setSelectedApplicant] = useState<PendingApplicant | null>(null)
  const [applicantDetails, setApplicantDetails] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [verifying, setVerifying] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [verificationNotes, setVerificationNotes] = useState("")
  const [verificationDecision, setVerificationDecision] = useState<"approve" | "reject" | "correct" | null>(null)

  useEffect(() => {
    fetchPendingApplicants()
  }, [])

  const fetchPendingApplicants = async () => {
    try {
      setLoading(true)
      const token = localStorage.getItem("access_token")
      const response = await axios.get(
        "/api/v1/admissions/wassce/pending",
        {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true,
        }
      )
      setPendingApplicants(response.data)
    } catch (err: any) {
      setError("Failed to load pending applications")
    } finally {
      setLoading(false)
    }
  }

  const handleSelectApplicant = async (applicant: PendingApplicant) => {
    setSelectedApplicant(applicant)
    setVerificationNotes("")
    setVerificationDecision(null)
    
    try {
      const token = localStorage.getItem("access_token")
      const response = await axios.get(
        `/api/v1/admissions/wassce/${applicant.applicant_id}/details`,
        {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true,
        }
      )
      setApplicantDetails(response.data)
    } catch (err: any) {
      setError("Failed to load applicant details")
    }
  }

  const handleSubmitVerification = async () => {
    if (!selectedApplicant || !verificationDecision) return

    try {
      setVerifying(true)
      const token = localStorage.getItem("access_token")

      if (verificationDecision === "approve") {
        await axios.post(
          `/api/v1/admissions/wassce/${selectedApplicant.applicant_id}/verify`,
          {
            verified: true,
            verification_notes: verificationNotes,
          },
          {
            headers: { Authorization: `Bearer ${token}` },
            withCredentials: true,
          }
        )
      } else if (verificationDecision === "reject") {
        await axios.post(
          `/api/v1/admissions/wassce/${selectedApplicant.applicant_id}/verify`,
          {
            verified: false,
            verification_notes: verificationNotes,
          },
          {
            headers: { Authorization: `Bearer ${token}` },
            withCredentials: true,
          }
        )
      } else if (verificationDecision === "correct") {
        await axios.post(
          `/api/v1/admissions/wassce/${selectedApplicant.applicant_id}/request-correction`,
          {
            reason: verificationNotes,
          },
          {
            headers: { Authorization: `Bearer ${token}` },
            withCredentials: true,
          }
        )
      }

      alert("Verification decision recorded")
      setSelectedApplicant(null)
      setApplicantDetails(null)
      await fetchPendingApplicants()
    } catch (err: any) {
      setError("Failed to record verification decision")
    } finally {
      setVerifying(false)
    }
  }

  if (loading && pendingApplicants.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading pending applications...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">WASSCE Verification</h1>
          <p className="text-gray-600 mt-1">Review and verify applicant WASSCE results</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Pending List */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">
                Pending Verification ({pendingApplicants.length})
              </h2>

              {pendingApplicants.length === 0 ? (
                <div className="p-4 bg-green-50 rounded-lg">
                  <p className="text-green-800 text-sm">
                    No pending WASSCE verifications at the moment.
                  </p>
                </div>
              ) : (
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {pendingApplicants.map((applicant) => (
                    <button
                      key={applicant.applicant_id}
                      onClick={() => handleSelectApplicant(applicant)}
                      className={`w-full text-left p-3 rounded-lg border-2 transition-colors ${
                        selectedApplicant?.applicant_id === applicant.applicant_id
                          ? "border-blue-600 bg-blue-50"
                          : "border-gray-200 hover:border-gray-300"
                      }`}
                    >
                      <div className="font-medium text-gray-900">
                        {applicant.first_name} {applicant.last_name}
                      </div>
                      <div className="text-xs text-gray-600">
                        Index: {applicant.index_number}
                      </div>
                      <div className="text-xs text-gray-500">
                        {new Date(applicant.submitted_at).toLocaleDateString()}
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Right: Details & Verification */}
          <div className="lg:col-span-2">
            {!selectedApplicant ? (
              <div className="bg-white rounded-lg shadow-md p-6 text-center">
                <p className="text-gray-600">
                  Select an applicant from the list to review their WASSCE results.
                </p>
              </div>
            ) : applicantDetails ? (
              <div className="bg-white rounded-lg shadow-md p-6">
                {/* Applicant Header */}
                <div className="mb-6 pb-6 border-b">
                  <h2 className="text-2xl font-bold text-gray-900">
                    {applicantDetails.full_name}
                  </h2>
                  <div className="mt-2 grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Index Number:</span>
                      <p className="font-medium text-gray-900">{applicantDetails.index_number}</p>
                    </div>
                    <div>
                      <span className="text-gray-600">Exam Year:</span>
                      <p className="font-medium text-gray-900">{applicantDetails.examination_year}</p>
                    </div>
                  </div>
                </div>

                {/* Results Table */}
                <div className="mb-6">
                  <h3 className="text-lg font-bold text-gray-900 mb-3">📊 Submitted Results</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-2 text-left font-medium text-gray-900">
                            Subject
                          </th>
                          <th className="px-4 py-2 text-left font-medium text-gray-900">
                            Grade
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(applicantDetails.submitted_results || {}).map(
                          ([subject, grade]: any) => (
                            <tr key={subject} className="border-t">
                              <td className="px-4 py-2 text-gray-900">{subject}</td>
                              <td className="px-4 py-2 font-medium text-blue-600">{grade as string}</td>
                            </tr>
                          )
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Evidence */}
                {applicantDetails.documents && applicantDetails.documents.length > 0 && (
                  <div className="mb-6">
                    <h3 className="text-lg font-bold text-gray-900 mb-3">📄 Supporting Documents</h3>
                    <ul className="space-y-2">
                      {applicantDetails.documents.map((doc: string) => (
                        <li key={doc} className="flex items-center gap-2">
                          <span>📎</span>
                          <a href={doc} className="text-blue-600 hover:underline">
                            View Document
                          </a>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Verification Form */}
                <div className="mb-6 pb-6 border-t">
                  <h3 className="text-lg font-bold text-gray-900 mb-4 mt-4">✅ Verification Decision</h3>

                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Verification Notes
                    </label>
                    <textarea
                      value={verificationNotes}
                      onChange={(e) => setVerificationNotes(e.target.value)}
                      placeholder="Enter your verification notes, findings, or reason for rejection/correction..."
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      rows={4}
                    ></textarea>
                  </div>

                  <div className="flex gap-3">
                    <Button
                      onClick={() => setVerificationDecision("approve")}
                      className={`flex-1 py-3 ${
                        verificationDecision === "approve"
                          ? "bg-green-600 hover:bg-green-700"
                          : "bg-gray-300 hover:bg-gray-400"
                      }`}
                      disabled={verifying}
                    >
                      ✓ Verify
                    </Button>
                    <Button
                      onClick={() => setVerificationDecision("correct")}
                      className={`flex-1 py-3 ${
                        verificationDecision === "correct"
                          ? "bg-yellow-600 hover:bg-yellow-700"
                          : "bg-gray-300 hover:bg-gray-400"
                      }`}
                      disabled={verifying}
                    >
                      ! Request Correction
                    </Button>
                    <Button
                      onClick={() => setVerificationDecision("reject")}
                      className={`flex-1 py-3 ${
                        verificationDecision === "reject"
                          ? "bg-red-600 hover:bg-red-700"
                          : "bg-gray-300 hover:bg-gray-400"
                      }`}
                      disabled={verifying}
                    >
                      ✕ Reject
                    </Button>
                  </div>

                  {verificationDecision && (
                    <div className="mt-4 flex gap-3">
                      <Button
                        onClick={() => setVerificationDecision(null)}
                        variant="outline"
                        className="flex-1"
                        disabled={verifying}
                      >
                        Cancel
                      </Button>
                      <Button
                        onClick={handleSubmitVerification}
                        disabled={verifying}
                        className="flex-1 bg-blue-600 hover:bg-blue-700"
                      >
                        {verifying ? "Recording..." : "Submit Decision"}
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-md p-6 text-center">
                <p className="text-gray-600">Loading applicant details...</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
