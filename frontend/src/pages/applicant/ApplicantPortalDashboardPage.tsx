/**
 * Applicant Portal Dashboard Page
 * Section 34: APPLICANT PORTAL - Dashboard (FEE-FIRST FLOW)
 * 
 * This page is gated by payment verification.
 * If payment is not verified, redirects to payment page.
 */

import React, { useState, useEffect } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { Button } from "@/components/ui/Button"
import axios from "axios"

interface DashboardData {
  applicant_id: string
  full_name: string
  application_status: string
  overall_progress: number
  sections_completed: number
  total_sections: number
  current_step: string
  can_submit: boolean
  submission_deadline?: string
  has_application: boolean
}

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-gray-100 text-gray-800",
  submitted: "bg-blue-100 text-blue-800",
  awaiting_results: "bg-yellow-100 text-yellow-800",
  results_uploaded: "bg-orange-100 text-orange-800",
  results_approved: "bg-green-100 text-green-800",
  payment_pending: "bg-yellow-100 text-yellow-800",
  payment_verified: "bg-green-100 text-green-800",
  eligible: "bg-green-100 text-green-800",
  ineligible: "bg-red-100 text-red-800",
  ranked: "bg-purple-100 text-purple-800",
  allocated: "bg-green-100 text-green-800",
  offered: "bg-blue-100 text-blue-800",
  accepted: "bg-green-100 text-green-800",
  rejected: "bg-red-100 text-red-800",
}

export default function ApplicantPortalDashboardPage() {
  const { schoolCode } = useParams<{ schoolCode: string }>()
  const navigate = useNavigate()
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [paymentRequired, setPaymentRequired] = useState(false)
  const [showMenu, setShowMenu] = useState(false)

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const token = localStorage.getItem("access_token")
        if (!token) {
          navigate(`/apply/${schoolCode}/login`)
          return
        }

        const response = await axios.get(
          `/api/v1/apply/${schoolCode}/dashboard`,
          {
            headers: { Authorization: `Bearer ${token}` },
            withCredentials: true,
          }
        )
        setDashboardData(response.data)
      } catch (err: any) {
        if (err.response?.status === 401) {
          navigate(`/apply/${schoolCode}/login`)
        } else if (err.response?.status === 402) {
          // Payment required gate (FEE-FIRST FLOW)
          setPaymentRequired(true)
          setError(err.response?.data?.detail || "Payment verification required")
        } else {
          setError("Failed to load dashboard")
        }
      } finally {
        setLoading(false)
      }
    }

    fetchDashboard()
  }, [schoolCode, navigate])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  // Payment required gate
  if (paymentRequired) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-yellow-50 to-orange-100 flex items-center justify-center px-4">
        <div className="bg-white p-8 rounded-lg shadow-xl max-w-md w-full text-center">
          <div className="text-5xl mb-4">⏳</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Payment Required</h1>
          <p className="text-gray-700 mb-6">
            {error || "Your application fee payment must be verified before you can access your application form."}
          </p>
          <Button
            onClick={() => navigate(`/apply/${schoolCode}/payment`)}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white mb-3"
          >
            Complete Payment
          </Button>
          <Button
            onClick={() => navigate(`/apply/${schoolCode}/login`)}
            variant="outline"
            className="w-full"
          >
            Back to Login
          </Button>
        </div>
      </div>
    )
  }

  if (error && !paymentRequired) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg max-w-md">
          <p className="text-red-600">{error}</p>
          <Button onClick={() => window.location.reload()} className="mt-4 w-full">
            Retry
          </Button>
        </div>
      </div>
    )
  }

  if (!dashboardData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">No dashboard data available</p>
        </div>
      </div>
    )
  }

  const handleLogout = () => {
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
    localStorage.removeItem("current_user")
    navigate(`/apply/${schoolCode}`)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Applicant Dashboard</h1>
            <p className="text-gray-600 mt-1">Welcome, {dashboardData.full_name}</p>
          </div>
          <div className="relative">
            <Button
              onClick={() => setShowMenu(!showMenu)}
              variant="outline"
              className="flex items-center gap-2"
            >
              <span className="text-lg">⚙️</span> Menu
            </Button>
            {showMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg z-10">
                <Button
                  onClick={() => navigate(`/apply/${schoolCode}/personal`)}
                  variant="ghost"
                  className="w-full justify-start rounded-none border-b"
                >
                  Edit Profile
                </Button>
                <Button
                  onClick={handleLogout}
                  variant="ghost"
                  className="w-full justify-start rounded-none text-red-600"
                >
                  Logout
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* Status Card */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Application Status</h2>
            <span className={`px-4 py-2 rounded-full text-sm font-semibold ${STATUS_COLORS[dashboardData.application_status] || "bg-gray-100 text-gray-800"}`}>
              {dashboardData.application_status.replace(/_/g, " ").toUpperCase()}
            </span>
          </div>

          {/* Progress Bar */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-700 font-medium">Application Progress</span>
              <span className="text-blue-600 font-bold">{dashboardData.overall_progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                style={{ width: `${dashboardData.overall_progress}%` }}
              ></div>
            </div>
            <p className="text-sm text-gray-600 mt-2">
              {dashboardData.sections_completed} of {dashboardData.total_sections} sections completed
            </p>
          </div>

          {dashboardData.submission_deadline && (
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-sm text-gray-700">
                <strong>Submission Deadline:</strong> {dashboardData.submission_deadline}
              </p>
            </div>
          )}
        </div>

        {/* OFFER BANNER — shown when status is offered or allocated */}
        {(dashboardData.application_status === "offered" || dashboardData.application_status === "allocated") && (
          <div className="bg-gradient-to-r from-green-500 to-emerald-600 rounded-lg shadow-lg p-8 mb-8 text-white">
            <div className="flex items-center gap-4 mb-4">
              <span className="text-5xl">🎓</span>
              <div>
                <h2 className="text-2xl font-bold">Congratulations! You Have Been Offered Admission</h2>
                <p className="text-green-100 mt-1">
                  You have been offered a place at the university. Please accept or decline your offer below.
                </p>
              </div>
            </div>
            <div className="flex flex-wrap gap-4 mt-6">
              <button
                id="accept-offer-btn"
                onClick={async () => {
                  try {
                    const token = localStorage.getItem("access_token")
                    await axios.post(
                      `/api/v1/apply/${schoolCode}/offer/accept`,
                      {},
                      { headers: { Authorization: `Bearer ${token}` }, withCredentials: true }
                    )
                    alert("🎉 Offer accepted! Welcome to the university. Your enrollment is now being processed.")
                    window.location.reload()
                  } catch (err: any) {
                    alert(err.response?.data?.detail || "Failed to accept offer. Please try again.")
                  }
                }}
                className="bg-white text-green-700 font-bold px-8 py-3 rounded-lg hover:bg-green-50 transition-colors shadow"
              >
                ✅ Accept Offer
              </button>
              <button
                id="decline-offer-btn"
                onClick={async () => {
                  if (!confirm("Are you sure you want to decline this offer?")) return
                  try {
                    const token = localStorage.getItem("access_token")
                    await axios.post(
                      `/api/v1/apply/${schoolCode}/offer/decline`,
                      {},
                      { headers: { Authorization: `Bearer ${token}` }, withCredentials: true }
                    )
                    alert("Offer declined. You can re-apply in the next admissions cycle.")
                    window.location.reload()
                  } catch (err: any) {
                    alert(err.response?.data?.detail || "Failed to decline offer.")
                  }
                }}
                className="bg-transparent border-2 border-white text-white font-bold px-8 py-3 rounded-lg hover:bg-green-600 transition-colors"
              >
                ❌ Decline Offer
              </button>
            </div>
          </div>
        )}

        {/* Enrolled banner */}
        {dashboardData.application_status === "enrolled" && (
          <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-lg shadow-lg p-8 mb-8 text-white">
            <div className="flex items-center gap-4">
              <span className="text-5xl">🎉</span>
              <div>
                <h2 className="text-2xl font-bold">You Are Now Enrolled!</h2>
                <p className="text-blue-100 mt-1">
                  Welcome to the university. Your student credentials have been sent to your email.
                </p>
              </div>
            </div>
          </div>
        )}


        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">📝 Application</h3>
            <p className="text-gray-600 mb-4">
              {dashboardData.has_application
                ? "Continue working on your application"
                : "Start your new application"}
            </p>
            <Button
              onClick={() => navigate(`/apply/${schoolCode}/application`)}
              className="w-full bg-blue-600 hover:bg-blue-700"
            >
              {dashboardData.has_application ? "Continue Application" : "Start Application"}
            </Button>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">📋 Review & Submit</h3>
            <p className="text-gray-600 mb-4">
              Review your application details before final submission
            </p>
            <Button
              onClick={() => navigate(`/apply/${schoolCode}/application?tab=statement`)}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white"
            >
              Review Application
            </Button>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">📄 Documents</h3>
            <p className="text-gray-600 mb-4">
              Upload required supporting documents
            </p>
            <Button
              onClick={() => navigate(`/apply/${schoolCode}/documents`)}
              variant="outline"
              className="w-full"
            >
              Manage Documents
            </Button>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">💰 Payment</h3>
            <p className="text-gray-600 mb-4">
              Pay application fees
            </p>
            <Button
              onClick={() => navigate(`/apply/${schoolCode}/payment`)}
              variant="outline"
              className="w-full"
            >
              Make Payment
            </Button>
          </div>
        </div>

        {/* Application Sections */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">📑 Application Sections</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div 
              onClick={() => navigate(`/apply/${schoolCode}/application`)}
              className="flex items-center p-3 border rounded-lg hover:bg-gray-50 cursor-pointer"
            >
              <span className="text-2xl mr-4">👤</span>
              <div className="flex-1">
                <p className="font-medium text-gray-900">Personal Information</p>
                <p className="text-sm text-gray-600">Name, contact details</p>
              </div>
              <span className="text-green-600">✓</span>
            </div>

            <div 
              onClick={() => navigate(`/apply/${schoolCode}/application`)}
              className="flex items-center p-3 border rounded-lg hover:bg-gray-50 cursor-pointer"
            >
              <span className="text-2xl mr-4">🎓</span>
              <div className="flex-1">
                <p className="font-medium text-gray-900">Academic Details</p>
                <p className="text-sm text-gray-600">WASSCE results, grades</p>
              </div>
              <span className={dashboardData.overall_progress >= 50 ? "text-green-600 font-bold" : "text-gray-400"}>
                {dashboardData.overall_progress >= 50 ? "✓" : "◯"}
              </span>
            </div>

            <div 
              onClick={() => navigate(`/apply/${schoolCode}/application`)}
              className="flex items-center p-3 border rounded-lg hover:bg-gray-50 cursor-pointer"
            >
              <span className="text-2xl mr-4">🏆</span>
              <div className="flex-1">
                <p className="font-medium text-gray-900">Programme Choices</p>
                <p className="text-sm text-gray-600">Select desired programmes</p>
              </div>
              <span className={dashboardData.overall_progress >= 75 ? "text-green-600 font-bold" : "text-gray-400"}>
                {dashboardData.overall_progress >= 75 ? "✓" : "◯"}
              </span>
            </div>

            <div 
              onClick={() => navigate(`/apply/${schoolCode}/application`)}
              className="flex items-center p-3 border rounded-lg hover:bg-gray-50 cursor-pointer"
            >
              <span className="text-2xl mr-4">✅</span>
              <div className="flex-1">
                <p className="font-medium text-gray-900">Review & Submit</p>
                <p className="text-sm text-gray-600">Final submission</p>
              </div>
              <span className={dashboardData.overall_progress >= 100 || dashboardData.application_status === "submitted" ? "text-green-600 font-bold" : "text-gray-400"}>
                {dashboardData.overall_progress >= 100 || dashboardData.application_status === "submitted" ? "✓" : "◯"}
              </span>
            </div>
          </div>
        </div>

        {/* Help Section */}
        <div className="mt-8 bg-blue-50 rounded-lg p-6 border border-blue-200">
          <h3 className="text-lg font-bold text-blue-900 mb-2">❓ Need Help?</h3>
          <p className="text-blue-800 mb-4">
            Check our <a href="#" className="font-semibold underline">FAQ</a> or contact{" "}
            <a href="mailto:admissions@university.edu" className="font-semibold underline">
              admissions@university.edu
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}
