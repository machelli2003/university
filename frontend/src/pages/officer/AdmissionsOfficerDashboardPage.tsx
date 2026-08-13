/**
 * Section 40: Admissions Officer Dashboard
 * 
 * Role-specific dashboard showing:
 * - Quick statistics (applications, verifications)
 * - Status breakdown
 * - Recent applications
 * - Pending WASSCE verifications
 * - SLA alerts
 * - Performance metrics
 */

import React, { useState, useEffect } from "react"
import { Button } from "@/components/ui/Button"
import axios from "axios"

interface DashboardData {
  total_applications: number
  total_pending_verification: number
  total_under_review: number
  total_eligible: number
  total_rejected: number
  status_breakdown: { status: string; count: number; percentage: number }[]
  recent_applications: {
    applicant_id: string
    full_name: string
    email: string
    phone: string
    application_date: string
    current_status: string
    verification_status: string
    time_in_current_state: number
    priority: string
  }[]
  pending_verifications: any[]
  under_review_applications: any[]
  applications_over_5_days: any[]
  applications_over_10_days: any[]
  avg_time_in_review_hours: number
  verification_completion_rate: number
}

export default function AdmissionsOfficerDashboardPage() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedTab, setSelectedTab] = useState<"overview" | "pending" | "review" | "alerts">(
    "overview"
  )

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem("access_token")
      const response = await axios.get(
        "/api/v1/officer/dashboard/admissions",
        {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true,
        }
      )
      setDashboardData(response.data)
    } catch (err: any) {
      setError("Failed to load dashboard data")
    } finally {
      setLoading(false)
    }
  }

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

  if (error || !dashboardData) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-700">{error || "Failed to load dashboard"}</p>
            <Button onClick={fetchDashboardData} className="mt-4">
              Retry
            </Button>
          </div>
        </div>
      </div>
    )
  }

  // Utility function to get status color
  const getStatusColor = (status: string): string => {
    const colorMap: Record<string, string> = {
      draft: "bg-gray-100 text-gray-800",
      submitted: "bg-blue-100 text-blue-800",
      payment_pending: "bg-yellow-100 text-yellow-800",
      payment_verified: "bg-green-100 text-green-800",
      under_review: "bg-purple-100 text-purple-800",
      department_review: "bg-indigo-100 text-indigo-800",
      eligible: "bg-green-100 text-green-800",
      ineligible: "bg-red-100 text-red-800",
      offered: "bg-blue-100 text-blue-800",
      rejected: "bg-red-100 text-red-800",
      enrolled: "bg-green-100 text-green-800",
    }
    return colorMap[status] || "bg-gray-100 text-gray-800"
  }

  const getPriorityColor = (priority: string): string => {
    switch (priority) {
      case "urgent":
        return "text-red-600 bg-red-50"
      case "high":
        return "text-yellow-600 bg-yellow-50"
      default:
        return "text-gray-600 bg-gray-50"
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Admissions Dashboard</h1>
              <p className="text-gray-600 mt-1">Manage applications and WASSCE verifications</p>
            </div>
            <Button onClick={fetchDashboardData} className="bg-blue-600 hover:bg-blue-700">
              🔄 Refresh
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-gray-600 text-sm font-medium">Total Applications</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">
              {dashboardData.total_applications}
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-gray-600 text-sm font-medium">Pending Verification</p>
            <p className="text-3xl font-bold text-yellow-600 mt-2">
              {dashboardData.total_pending_verification}
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-gray-600 text-sm font-medium">Under Review</p>
            <p className="text-3xl font-bold text-purple-600 mt-2">
              {dashboardData.total_under_review}
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-gray-600 text-sm font-medium">Eligible</p>
            <p className="text-3xl font-bold text-green-600 mt-2">
              {dashboardData.total_eligible}
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-gray-600 text-sm font-medium">Rejected</p>
            <p className="text-3xl font-bold text-red-600 mt-2">
              {dashboardData.total_rejected}
            </p>
          </div>
        </div>

        {/* Metrics Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-gray-900 font-semibold mb-2">⏱️ Avg Review Time</p>
            <p className="text-4xl font-bold text-blue-600">
              {dashboardData.avg_time_in_review_hours.toFixed(1)}h
            </p>
            <p className="text-gray-600 text-sm mt-2">Average hours from submission to decision</p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-gray-900 font-semibold mb-2">✅ Verification Rate</p>
            <p className="text-4xl font-bold text-green-600">
              {dashboardData.verification_completion_rate.toFixed(1)}%
            </p>
            <p className="text-gray-600 text-sm mt-2">WASSCE results verified</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setSelectedTab("overview")}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              selectedTab === "overview"
                ? "bg-blue-600 text-white"
                : "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50"
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setSelectedTab("pending")}
            className={`px-4 py-2 rounded-lg font-medium transition-colors relative ${
              selectedTab === "pending"
                ? "bg-blue-600 text-white"
                : "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50"
            }`}
          >
            Pending Verification
            {dashboardData.total_pending_verification > 0 && (
              <span className="ml-2 bg-red-500 text-white rounded-full px-2 py-1 text-xs">
                {dashboardData.total_pending_verification}
              </span>
            )}
          </button>
          <button
            onClick={() => setSelectedTab("review")}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              selectedTab === "review"
                ? "bg-blue-600 text-white"
                : "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50"
            }`}
          >
            Under Review
          </button>
          <button
            onClick={() => setSelectedTab("alerts")}
            className={`px-4 py-2 rounded-lg font-medium transition-colors relative ${
              selectedTab === "alerts"
                ? "bg-blue-600 text-white"
                : "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50"
            }`}
          >
            SLA Alerts
            {dashboardData.applications_over_10_days.length > 0 && (
              <span className="ml-2 bg-red-500 text-white rounded-full px-2 py-1 text-xs">
                {dashboardData.applications_over_10_days.length}
              </span>
            )}
          </button>
        </div>

        {/* Overview Tab */}
        {selectedTab === "overview" && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Status Breakdown */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Status Breakdown</h2>
              <div className="space-y-3">
                {dashboardData.status_breakdown.slice(0, 10).map((item) => (
                  <div key={item.status} className="flex items-center gap-3">
                    <div className="flex-1">
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm font-medium text-gray-700">{item.status}</span>
                        <span className="text-sm text-gray-600">{item.count}</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ width: `${item.percentage}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Applications */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Applications</h2>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {dashboardData.recent_applications.slice(0, 5).map((app) => (
                  <div key={app.applicant_id} className="p-3 border rounded-lg hover:bg-gray-50">
                    <div className="font-medium text-gray-900">{app.full_name}</div>
                    <div className="text-xs text-gray-600">{app.email}</div>
                    <div className="flex gap-2 mt-2">
                      <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(app.current_status)}`}>
                        {app.current_status}
                      </span>
                      <span className="text-xs text-gray-600">
                        {new Date(app.application_date).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Pending Verification Tab */}
        {selectedTab === "pending" && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Pending WASSCE Verification</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left font-medium text-gray-900">Name</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-900">Email</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-900">Index</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-900">Submitted</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-900">Priority</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-900">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {dashboardData.pending_verifications.map((app) => (
                    <tr key={app.applicant_id} className="border-t hover:bg-gray-50">
                      <td className="px-4 py-3 font-medium text-gray-900">{app.full_name}</td>
                      <td className="px-4 py-3 text-gray-600">{app.email}</td>
                      <td className="px-4 py-3 text-gray-600">{app.applicant_id.slice(0, 8)}</td>
                      <td className="px-4 py-3 text-gray-600">
                        {new Date(app.application_date).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 text-xs rounded-full font-medium ${getPriorityColor(app.priority)}`}>
                          {app.priority}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
                          Review
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {dashboardData.pending_verifications.length === 0 && (
                <div className="p-6 text-center text-gray-600">No pending verifications</div>
              )}
            </div>
          </div>
        )}

        {/* Under Review Tab */}
        {selectedTab === "review" && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Applications Under Review</h2>
            <div className="space-y-3">
              {dashboardData.under_review_applications.map((app) => (
                <div key={app.applicant_id} className="p-4 border rounded-lg hover:bg-gray-50">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-semibold text-gray-900">{app.full_name}</div>
                      <div className="text-sm text-gray-600">{app.email}</div>
                      <div className="text-sm text-gray-600">{app.phone}</div>
                    </div>
                    <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
                      View Details
                    </Button>
                  </div>
                  <div className="mt-3 flex gap-2">
                    <span className={`px-2 py-1 text-xs rounded ${getStatusColor(app.current_status)}`}>
                      {app.current_status}
                    </span>
                    <span className="text-xs text-gray-600">
                      {app.time_in_current_state}h in this state
                    </span>
                  </div>
                </div>
              ))}
              {dashboardData.under_review_applications.length === 0 && (
                <div className="p-6 text-center text-gray-600">No applications under review</div>
              )}
            </div>
          </div>
        )}

        {/* Alerts Tab */}
        {selectedTab === "alerts" && (
          <div className="space-y-6">
            {/* Over 10 Days - Critical */}
            {dashboardData.applications_over_10_days.length > 0 && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                <h3 className="text-lg font-bold text-red-900 mb-4">
                  🚨 CRITICAL: Applications Stuck 10+ Days
                </h3>
                <div className="space-y-3">
                  {dashboardData.applications_over_10_days.map((app) => (
                    <div key={app.applicant_id} className="flex justify-between items-center p-3 bg-white rounded border-l-4 border-red-600">
                      <div>
                        <div className="font-medium text-gray-900">{app.full_name}</div>
                        <div className="text-sm text-gray-600">{app.current_status}</div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-red-600">{app.time_in_current_state}h</div>
                        <Button size="sm" className="mt-2 bg-red-600 hover:bg-red-700">
                          Escalate
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Over 5 Days - High Priority */}
            {dashboardData.applications_over_5_days.length > 0 && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
                <h3 className="text-lg font-bold text-yellow-900 mb-4">
                  ⚠️ HIGH PRIORITY: Applications Stuck 5+ Days
                </h3>
                <div className="space-y-3">
                  {dashboardData.applications_over_5_days.slice(0, 10).map((app) => (
                    <div key={app.applicant_id} className="flex justify-between items-center p-3 bg-white rounded border-l-4 border-yellow-600">
                      <div>
                        <div className="font-medium text-gray-900">{app.full_name}</div>
                        <div className="text-sm text-gray-600">{app.current_status}</div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-yellow-600">{app.time_in_current_state}h</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {dashboardData.applications_over_5_days.length === 0 && dashboardData.applications_over_10_days.length === 0 && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
                <p className="text-green-800 font-medium">✅ No SLA alerts - all applications on track!</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
