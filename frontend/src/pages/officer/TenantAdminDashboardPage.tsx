import React, { useEffect, useState } from "react"
import { useAuthStore } from "@/store/authStore"
import axios from "axios"
import { Button } from "@/components/ui/Button"
import { Card } from "@/components/ui/Card"

interface UserInfo {
  user_id: string
  name: string
  email: string
  role: string
  status: "active" | "inactive"
}

interface PendingApproval {
  approval_id: string
  request_type: string
  requester_name: string
  submitted_date: string
}

interface TenantAdminDashboardData {
  total_users: number
  active_users: number
  system_health: number
  pending_approvals: number
  users: UserInfo[]
  pending_requests: PendingApproval[]
}

export default function TenantAdminDashboardPage() {
  const { user } = useAuthStore()
  const [data, setData] = useState<TenantAdminDashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedTab, setSelectedTab] = useState<"overview" | "users" | "approvals" | "system">("overview")

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const token = localStorage.getItem("access_token")
        if (!token) return

        const response = await axios.get(`/api/v1/officer/dashboard/tenant_admin`, {
          headers: { Authorization: `Bearer ${token}` },
        })

        setData(response.data)
      } catch (error) {
        console.error("Failed to load TenantAdmin dashboard:", error)
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
          <h1 className="text-3xl font-bold text-gray-900">Tenant Administration Dashboard</h1>
          <p className="text-gray-600 mt-2">Welcome, {user?.first_name || "Tenant Admin"}</p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Total Users</div>
            <div className="mt-2 text-3xl font-bold text-blue-600">{data.total_users}</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Active Users</div>
            <div className="mt-2 text-3xl font-bold text-green-600">{data.active_users}</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">System Health</div>
            <div className="mt-2 text-3xl font-bold text-purple-600">{data.system_health}%</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Pending Approvals</div>
            <div className="mt-2 text-3xl font-bold text-orange-600">{data.pending_approvals}</div>
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
              onClick={() => setSelectedTab("users")}
              className={`px-6 py-4 font-medium ${
                selectedTab === "users"
                  ? "border-b-2 border-blue-600 text-blue-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Users
            </button>
            <button
              onClick={() => setSelectedTab("approvals")}
              className={`px-6 py-4 font-medium ${
                selectedTab === "approvals"
                  ? "border-b-2 border-blue-600 text-blue-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Approvals
            </button>
            <button
              onClick={() => setSelectedTab("system")}
              className={`px-6 py-4 font-medium ${
                selectedTab === "system"
                  ? "border-b-2 border-blue-600 text-blue-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              System
            </button>
          </div>

          <div className="p-6">
            {/* Overview Tab */}
            {selectedTab === "overview" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Tenant Overview</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-lg">
                      <div className="text-sm text-gray-600">Total Users</div>
                      <div className="text-3xl font-bold text-blue-600 mt-2">{data.total_users}</div>
                      <p className="text-sm text-gray-600 mt-2">Active: {data.active_users}</p>
                    </div>

                    <div className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-lg">
                      <div className="text-sm text-gray-600">System Health</div>
                      <div className="text-3xl font-bold text-green-600 mt-2">{data.system_health}%</div>
                      <p className="text-sm text-gray-600 mt-2">All systems operational</p>
                    </div>

                    <div className="bg-gradient-to-br from-orange-50 to-orange-100 p-6 rounded-lg">
                      <div className="text-sm text-gray-600">Pending Items</div>
                      <div className="text-3xl font-bold text-orange-600 mt-2">{data.pending_approvals}</div>
                      <p className="text-sm text-gray-600 mt-2">Requiring review</p>
                    </div>
                  </div>
                </div>

                <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-6 rounded-lg">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">System Status</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-700">Database</span>
                      <span className="font-semibold text-green-600">Healthy</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-700">API Servers</span>
                      <span className="font-semibold text-green-600">Online</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-700">Backup Status</span>
                      <span className="font-semibold text-green-600">Current</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Users Tab */}
            {selectedTab === "users" && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Tenant Users</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Name</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Email</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Role</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Status</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.users.map((user) => (
                        <tr key={user.user_id} className="border-b hover:bg-gray-50">
                          <td className="py-3 px-4 text-gray-900 font-medium">{user.name}</td>
                          <td className="py-3 px-4 text-gray-700">{user.email}</td>
                          <td className="py-3 px-4 text-gray-700">{user.role}</td>
                          <td className="py-3 px-4">
                            <span
                              className={`px-3 py-1 rounded-full text-sm font-medium ${
                                user.status === "active"
                                  ? "bg-green-100 text-green-800"
                                  : "bg-gray-100 text-gray-800"
                              }`}
                            >
                              {user.status.charAt(0).toUpperCase() + user.status.slice(1)}
                            </span>
                          </td>
                          <td className="py-3 px-4">
                            <Button className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 text-sm">
                              Manage
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Approvals Tab */}
            {selectedTab === "approvals" && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Pending Approvals ({data.pending_approvals})</h3>
                <div className="space-y-3">
                  {data.pending_requests.map((request) => (
                    <div key={request.approval_id} className="p-4 border rounded-lg hover:shadow-md transition">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="font-semibold text-gray-900">{request.request_type}</div>
                          <div className="text-sm text-gray-600">From: {request.requester_name}</div>
                          <div className="text-sm text-gray-600">Submitted: {request.submitted_date}</div>
                        </div>
                        <div className="flex gap-2">
                          <Button className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 text-sm">
                            Approve
                          </Button>
                          <Button className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 text-sm">
                            Reject
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* System Tab */}
            {selectedTab === "system" && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">System Configuration</h3>
                <div className="space-y-4">
                  <div className="p-4 bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg">
                    <div className="flex justify-between items-center">
                      <div>
                        <div className="font-semibold text-gray-900">Database</div>
                        <div className="text-sm text-gray-600">Primary MongoDB instance</div>
                      </div>
                      <div className="text-green-600 font-semibold">✓ Healthy</div>
                    </div>
                  </div>

                  <div className="p-4 bg-gradient-to-r from-green-50 to-green-100 rounded-lg">
                    <div className="flex justify-between items-center">
                      <div>
                        <div className="font-semibold text-gray-900">API Services</div>
                        <div className="text-sm text-gray-600">FastAPI backend servers</div>
                      </div>
                      <div className="text-green-600 font-semibold">✓ Online</div>
                    </div>
                  </div>

                  <div className="p-4 bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg">
                    <div className="flex justify-between items-center">
                      <div>
                        <div className="font-semibold text-gray-900">Backups</div>
                        <div className="text-sm text-gray-600">Last backup 2 hours ago</div>
                      </div>
                      <div className="text-green-600 font-semibold">✓ Current</div>
                    </div>
                  </div>

                  <div className="p-4 border-t">
                    <Button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 mr-2">
                      System Settings
                    </Button>
                    <Button className="bg-gray-600 hover:bg-gray-700 text-white px-6 py-2">
                      View Logs
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
