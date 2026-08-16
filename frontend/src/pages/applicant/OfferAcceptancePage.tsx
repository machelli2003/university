/**
 * Applicant Offer Acceptance & Enrollment
 * Section 61: Student Lifecycle - Applicant → Student Conversion
 * 
 * When applicant accepts offer:
 * - Enrollment record created
 * - Student record created (if needed)
 * - Student ID generated
 * - Student portal access created
 * - Academic profile initialized
 */

import React, { useState, useEffect } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { Button } from "@/components/ui/Button"
import axios from "axios"
import { CheckCircle2, AlertCircle, Clock, Download } from "lucide-react"

interface AdmissionOffer {
  offer_id: string
  applicant_id: string
  applicant_name: string
  programme_name: string
  programme_code: string
  offer_date: string
  expiry_date: string
  conditions?: string[]
  acceptance_deadline: string
}

interface EnrollmentStatus {
  status: "pending" | "completed" | "error"
  student_id?: string
  message: string
  details?: any
}

export default function OfferAcceptancePage() {
  const { offerId } = useParams<{ offerId: string }>()
  const navigate = useNavigate()
  const [offer, setOffer] = useState<AdmissionOffer | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [accepting, setAccepting] = useState(false)
  const [enrollmentStatus, setEnrollmentStatus] = useState<EnrollmentStatus | null>(null)
  const [termsAccepted, setTermsAccepted] = useState(false)

  useEffect(() => {
    loadOffer()
  }, [offerId])

  async function loadOffer() {
    try {
      setLoading(true)
      const token = localStorage.getItem("access_token")
      const response = await axios.get(`/api/v1/admissions/offers/${offerId}`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true,
      })
      setOffer(response.data)
    } catch (err: any) {
      setError("Failed to load offer")
    } finally {
      setLoading(false)
    }
  }

  async function handleAcceptOffer() {
    if (!offer || !termsAccepted) return
    setAccepting(true)
    setEnrollmentStatus(null)

    try {
      const token = localStorage.getItem("access_token")

      // Step 1: Accept offer
      const offerResponse = await axios.post(
        `/api/v1/admissions/offers/${offer.offer_id}/accept`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true,
        }
      )

      // Step 2: Initiate enrollment (this triggers student creation and ID generation)
      const enrollResponse = await axios.post(
        `/api/v1/admissions/applicants/${offer.applicant_id}/enroll`,
        { programme_code: offer.programme_code },
        {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true,
        }
      )

      setEnrollmentStatus({
        status: "completed",
        student_id: enrollResponse.data.student_id,
        message: `Welcome! Your student account has been created. Your Student ID is ${enrollResponse.data.student_id}`,
        details: enrollResponse.data,
      })

      setTimeout(() => {
        navigate(`/apply/${offer.programme_code.substring(0, 4).toLowerCase()}/enrollment-complete/${enrollResponse.data.student_id}`)
      }, 3000)
    } catch (err: any) {
      setEnrollmentStatus({
        status: "error",
        message: err.response?.data?.detail || "Failed to process enrollment",
      })
      setError(err.response?.data?.detail || "Enrollment failed")
    } finally {
      setAccepting(false)
    }
  }

  if (loading)
    return (
      <div className="min-h-screen bg-gradient-to-b from-cocoa-50 to-white flex items-center justify-center">
        <div className="text-center">
          <Clock className="h-8 w-8 text-cocoa-600 mx-auto mb-2 animate-spin" />
          <p className="text-cocoa-600">Loading offer...</p>
        </div>
      </div>
    )

  if (error || !offer)
    return (
      <div className="min-h-screen bg-gradient-to-b from-cocoa-50 to-white flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md text-center">
          <AlertCircle className="h-8 w-8 text-red-600 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-ink mb-2">Error Loading Offer</h2>
          <p className="text-cocoa-600 mb-6">{error || "Offer not found"}</p>
          <Button onClick={() => navigate(-1)} variant="secondary" className="w-full">
            Go Back
          </Button>
        </div>
      </div>
    )

  if (enrollmentStatus?.status === "completed")
    return (
      <div className="min-h-screen bg-gradient-to-b from-green-50 to-white flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md text-center">
          <CheckCircle2 className="h-12 w-12 text-green-600 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-ink mb-2">Enrollment Successful!</h2>
          <p className="text-cocoa-600 mb-4">{enrollmentStatus.message}</p>
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
            <p className="text-xs font-medium text-green-800 mb-1">STUDENT ID</p>
            <p className="text-2xl font-bold text-green-700">{enrollmentStatus.student_id}</p>
          </div>
          <p className="text-sm text-cocoa-500 mb-6">Redirecting to your student portal...</p>
        </div>
      </div>
    )

  const deadlineDate = new Date(offer.acceptance_deadline)
  const isExpiringSoon = deadlineDate.getTime() - Date.now() < 7 * 24 * 60 * 60 * 1000

  return (
    <div className="min-h-screen bg-gradient-to-b from-cocoa-50 to-white py-12">
      <div className="max-w-2xl mx-auto px-4">
        {/* HEADER */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-ink mb-2">🎉 Admission Offer</h1>
          <p className="text-cocoa-600">Congratulations on your admission!</p>
        </div>

        {/* OFFER CARD */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
          <div className="border-b border-cocoa-100 pb-6 mb-6">
            <h2 className="text-2xl font-bold text-ink mb-2">{offer.applicant_name}</h2>
            <p className="text-cocoa-600">Admitted to: {offer.programme_name}</p>
          </div>

          <div className="grid gap-6 md:grid-cols-2 mb-8">
            <div>
              <p className="text-xs font-medium text-cocoa-600 uppercase mb-1">Offer Date</p>
              <p className="text-lg font-semibold text-ink">{new Date(offer.offer_date).toLocaleDateString()}</p>
            </div>
            <div>
              <p className="text-xs font-medium text-cocoa-600 uppercase mb-1">Programme Code</p>
              <p className="text-lg font-semibold text-ink">{offer.programme_code}</p>
            </div>
            <div>
              <p className="text-xs font-medium text-cocoa-600 uppercase mb-1">Expiry Date</p>
              <p className="text-lg font-semibold text-ink">{new Date(offer.expiry_date).toLocaleDateString()}</p>
            </div>
            <div>
              <p className="text-xs font-medium text-cocoa-600 uppercase mb-1">Acceptance Deadline</p>
              <p className={`text-lg font-semibold ${isExpiringSoon ? "text-red-600" : "text-ink"}`}>
                {new Date(offer.acceptance_deadline).toLocaleDateString()}
              </p>
              {isExpiringSoon && (
                <p className="text-xs text-red-600 mt-1">⚠️ Expiring soon!</p>
              )}
            </div>
          </div>

          {/* CONDITIONS */}
          {offer.conditions && offer.conditions.length > 0 && (
            <div className="mb-8 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <h3 className="font-semibold text-ink mb-3">📋 Conditions of Admission</h3>
              <ul className="space-y-2">
                {offer.conditions.map((condition, idx) => (
                  <li key={idx} className="flex gap-3 text-sm text-cocoa-700">
                    <span className="text-yellow-600 font-bold">•</span>
                    <span>{condition}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* ERROR STATE */}
          {enrollmentStatus?.status === "error" && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-700">{enrollmentStatus.message}</p>
            </div>
          )}

          {/* TERMS ACCEPTANCE */}
          <div className="mb-6 p-4 bg-cocoa-50 border border-cocoa-200 rounded-lg">
            <label className="flex items-start gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={termsAccepted}
                onChange={(e) => setTermsAccepted(e.target.checked)}
                className="mt-1 w-4 h-4 border-cocoa-300 rounded"
              />
              <span className="text-sm text-cocoa-700">
                I accept this admission offer and agree to the conditions of admission. I understand that I must complete
                the enrollment process to secure my place.
              </span>
            </label>
          </div>

          {/* ACTIONS */}
          <div className="flex gap-3">
            <Button
              onClick={handleAcceptOffer}
              disabled={accepting || !termsAccepted}
              variant="primary"
              className="flex-1 bg-green-600 hover:bg-green-700"
            >
              {accepting ? "Processing Enrollment..." : "Accept Offer & Enroll"}
            </Button>
            <Button onClick={() => navigate(-1)} variant="secondary" className="flex-1">
              Decline
            </Button>
          </div>
        </div>

        {/* INFO */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-semibold text-blue-900 mb-2">ℹ️ Next Steps</h4>
          <ol className="text-sm text-blue-800 space-y-1 list-decimal list-inside">
            <li>Accept this offer</li>
            <li>Complete the enrollment process</li>
            <li>Receive your Student ID</li>
            <li>Access your student portal</li>
            <li>Register for courses before the registration deadline</li>
          </ol>
        </div>
      </div>
    </div>
  )
}
