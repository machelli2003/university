import React, { useEffect, useState } from "react"
import { useAuthStore } from "@/store/authStore"
import axios from "axios"
import { Button } from "@/components/ui/Button"
import { Card } from "@/components/ui/Card"

interface HostelInfo {
  hostel_id: string
  hostel_name: string
  total_beds: number
  occupied_beds: number
}

interface MaintenanceRequest {
  request_id: string
  hostel_name: string
  issue: string
  status: "pending" | "in-progress" | "completed"
  submitted_date: string
}

interface BedRequest {
  request_id: string
  student_name: string
  hostel_preference: string
  status: "approved" | "pending" | "rejected"
}

interface HostelDashboardData {
  total_hostels: number
  total_beds: number
  occupied_beds: number
  occupancy_rate: number
  pending_requests: number
  pending_maintenance: number
  hostels: HostelInfo[]
  maintenance_requests: MaintenanceRequest[]
  bed_requests: BedRequest[]
}

export default function HostelAdminDashboardPage() {
  const { user } = useAuthStore()
  const [data, setData] = useState<HostelDashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedTab, setSelectedTab] = useState<"overview" | "occupancy" | "maintenance" | "requests">("overview")

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const token = localStorage.getItem("access_token")
        if (!token) return

        const response = await axios.get(`/api/v1/officer/dashboard/hostel`, {
          headers: { Authorization: `Bearer ${token}` },
        })

        setData(response.data)
      } catch (error) {
        console.error("Failed to load Hostel dashboard:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchDashboard()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg text-gray-600">Loading dashboard...</div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg text-red-600">Failed to load dashboard data</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Hostel Administration Dashboard</h1>
          <p className="text-gray-600 mt-2">Welcome, {user?.first_name || "Hostel Admin"}</p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Hostels</div>
            <div className="mt-2 text-3xl font-bold text-blue-600">{data.total_hostels}</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Total Beds</div>
            <div className="mt-2 text-3xl font-bold text-green-600">{data.total_beds}</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Occupied</div>
            <div className="mt-2 text-3xl font-bold text-purple-600">{data.occupied_beds}</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Occupancy Rate</div>
            <div className="mt-2 text-3xl font-bold text-orange-600">{data.occupancy_rate.toFixed(1)}%</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Pending Issues</div>
            <div className="mt-2 text-3xl font-bold text-red-600">{data.pending_maintenance}</div>
          </Card>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow">
          <div className="flex border-b">
            <button
              onClick={() => setSelectedTab("overview")}
              className={`px-6 py-4 font-medium ${
                selectedTab === "overview"
                  ? "border-b-2 border-blue-600 text-blue-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setSelectedTab("occupancy")}
              className={`px-6 py-4 font-medium ${
                selectedTab === "occupancy"
                  ? "border-b-2 border-blue-600 text-blue-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Occupancy
            </button>
            <button
              onClick={() => setSelectedTab("maintenance")}
              className={`px-6 py-4 font-medium ${
                selectedTab === "maintenance"
                  ? "border-b-2 border-blue-600 text-blue-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Maintenance
            </button>
            <button
              onClick={() => setSelectedTab("requests")}
              className={`px-6 py-4 font-medium ${
                selectedTab === "requests"
                  ? "border-b-2 border-blue-600 text-blue-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Requests
            </button>
          </div>

          <div className="p-6">
            {/* Overview Tab */}
            {selectedTab === "overview" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Hostel System Overview</h3>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="bg-blue-50 p-4 rounded">
                      <div className="text-sm text-gray-600">Total Hostels</div>
                      <div className="text-2xl font-bold text-blue-600 mt-1">{data.total_hostels}</div>
                    </div>
                    <div className="bg-green-50 p-4 rounded">
                      <div className="text-sm text-gray-600">Total Beds</div>
                      <div className="text-2xl font-bold text-green-600 mt-1">{data.total_beds}</div>
                    </div>
                    <div className="bg-purple-50 p-4 rounded">
                      <div className="text-sm text-gray-600">Occupied Beds</div>
                      <div className="text-2xl font-bold text-purple-600 mt-1">{data.occupied_beds}</div>
                    </div>
                    <div className="bg-orange-50 p-4 rounded">
                      <div className="text-sm text-gray-600">Available Beds</div>
                      <div className="text-2xl font-bold text-orange-600 mt-1">{data.total_beds - data.occupied_beds}</div>
                    </div>
                  </div>
                </div>

                <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-6 rounded-lg">
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">Overall Occupancy Rate</h3>
                      <p className="text-sm text-gray-600 mt-1">
                        {data.occupied_beds} of {data.total_beds} beds occupied
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-4xl font-bold text-blue-600">{data.occupancy_rate.toFixed(1)}%</div>
                    </div>
                  </div>
                  <div className="w-full bg-blue-200 rounded-full h-3 mt-4">
                    <div
                      className="bg-blue-600 h-3 rounded-full"
                      style={{
                        width: `${Math.min(data.occupancy_rate, 100)}%`,
                      }}
                    ></div>
                  </div>
                </div>
              </div>
            )}

            {/* Occupancy Tab */}
            {selectedTab === "occupancy" && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Hostel Occupancy Details</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {data.hostels.map((hostel) => {
                    const occupancyPercent = (hostel.occupied_beds / hostel.total_beds) * 100
                    return (
                      <div key={hostel.hostel_id} className="p-4 border rounded-lg hover:shadow-md transition">
                        <div className="flex items-center justify-between mb-3">
                          <div className="font-semibold text-gray-900">{hostel.hostel_name}</div>
                          <span className="text-sm font-medium text-gray-600">{occupancyPercent.toFixed(0)}%</span>
                        </div>
                        <div className="text-sm text-gray-600 mb-2">
                          {hostel.occupied_beds}/{hostel.total_beds} beds
                        </div>
                        <div className="w-full bg-gray-300 rounded-full h-2">
                          <div
                            className="bg-green-500 h-2 rounded-full"
                            style={{
                              width: `${Math.min(occupancyPercent, 100)}%`,
                            }}
                          ></div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            )}

            {/* Maintenance Tab */}
            {selectedTab === "maintenance" && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Maintenance Requests</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Request ID</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Hostel</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Issue</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Date</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Status</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.maintenance_requests.map((request) => (
                        <tr key={request.request_id} className="border-b hover:bg-gray-50">
                          <td className="py-3 px-4 text-gray-900">{request.request_id.substring(0, 8)}</td>
                          <td className="py-3 px-4 text-gray-700">{request.hostel_name}</td>
                          <td className="py-3 px-4 text-gray-700">{request.issue}</td>
                          <td className="py-3 px-4 text-gray-700">{request.submitted_date}</td>
                          <td className="py-3 px-4">
                            <span
                              className={`px-3 py-1 rounded-full text-sm font-medium ${
                                request.status === "completed"
                                  ? "bg-green-100 text-green-800"
                                  : request.status === "in-progress"
                                    ? "bg-yellow-100 text-yellow-800"
                                    : "bg-red-100 text-red-800"
                              }`}
                            >
                              {request.status.charAt(0).toUpperCase() + request.status.slice(1)}
                            </span>
                          </td>
                          <td className="py-3 px-4">
                            <Button className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 text-sm">
                              View
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Requests Tab */}
            {selectedTab === "requests" && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Bed Requests ({data.pending_requests})</h3>
                <div className="space-y-3">
                  {data.bed_requests.map((request) => (
                    <div key={request.request_id} className="p-4 border rounded-lg hover:shadow-md transition">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="font-semibold text-gray-900">{request.student_name}</div>
                          <div className="text-sm text-gray-600">Prefers: {request.hostel_preference}</div>
                        </div>
                        <div className="flex items-center gap-2">
                          <span
                            className={`px-3 py-1 rounded-full text-sm font-medium ${
                              request.status === "approved"
                                ? "bg-green-100 text-green-800"
                                : request.status === "pending"
                                  ? "bg-yellow-100 text-yellow-800"
                                  : "bg-red-100 text-red-800"
                            }`}
                          >
                            {request.status.charAt(0).toUpperCase() + request.status.slice(1)}
                          </span>
                          <Button className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 text-sm">
                            Review
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
