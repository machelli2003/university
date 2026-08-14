import React, { useEffect, useState } from "react"
import { useAuthStore } from "@/store/authStore"
import { apiClient } from "@/services/api/client"
import { Button } from "@/components/ui/Button"
import { Card } from "@/components/ui/Card"

interface TenantInfo {
  tenant_id: string
  school_code: string
  school_name: string
  active_users: number
  status: "active" | "inactive"
}

interface SuperAdminDashboardData {
  total_tenants: number
  active_tenants: number
  total_system_users: number
  system_health: number
  total_data_usage_gb: number
  tenants: TenantInfo[]
}

export default function SuperAdminDashboardPage() {
  const { user } = useAuthStore()
  const accessToken = useAuthStore((s) => s.accessToken)
  const [data, setData] = useState<SuperAdminDashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedTab, setSelectedTab] = useState<"overview" | "tenants" | "metrics" | "settings">("overview")

  useEffect(() => {
    if (!accessToken) {
      // Store not yet hydrated — wait
      return
    }
    const fetchDashboard = async () => {
      try {
        const response = await apiClient.get<SuperAdminDashboardData>("/officer/dashboard/super_admin")
        setData(response.data)
      } catch (err: any) {
        const msg = err?.response?.data?.detail || err?.message || "Unknown error"
        console.error("Failed to load SuperAdmin dashboard:", err)
        setError(msg)
      } finally {
        setLoading(false)
      }
    }

    fetchDashboard()
  }, [accessToken])

  if (loading || !accessToken) {
    return (
      <div className="flex items-center justify-center min-h-[300px]">
        <div className="text-lg text-gray-600">Loading dashboard...</div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[300px] gap-4">
        <div className="text-lg text-red-600">Failed to load dashboard data</div>
        {error && <div className="text-sm text-gray-500 bg-red-50 border border-red-200 rounded px-4 py-2 max-w-lg text-center">{error}</div>}
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Super Admin Dashboard</h1>
          <p className="text-gray-600 mt-2">Welcome, {user?.first_name || "Super Admin"}</p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Total Tenants</div>
            <div className="mt-2 text-3xl font-bold text-blue-600">{data.total_tenants}</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Active Tenants</div>
            <div className="mt-2 text-3xl font-bold text-green-600">{data.active_tenants}</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">System Users</div>
            <div className="mt-2 text-3xl font-bold text-purple-600">{data.total_system_users}</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">System Health</div>
            <div className="mt-2 text-3xl font-bold text-orange-600">{data.system_health}%</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Data Usage</div>
            <div className="mt-2 text-3xl font-bold text-red-600">{data.total_data_usage_gb}GB</div>
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
              onClick={() => setSelectedTab("tenants")}
              className={`px-6 py-4 font-medium ${
                selectedTab === "tenants"
                  ? "border-b-2 border-blue-600 text-blue-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Tenants
            </button>
            <button
              onClick={() => setSelectedTab("metrics")}
              className={`px-6 py-4 font-medium ${
                selectedTab === "metrics"
                  ? "border-b-2 border-blue-600 text-blue-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Metrics
            </button>
            <button
              onClick={() => setSelectedTab("settings")}
              className={`px-6 py-4 font-medium ${
                selectedTab === "settings"
                  ? "border-b-2 border-blue-600 text-blue-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Settings
            </button>
          </div>

          <div className="p-6">
            {/* Overview Tab */}
            {selectedTab === "overview" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Platform Overview</h3>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="bg-blue-50 p-4 rounded">
                      <div className="text-sm text-gray-600">Total Tenants</div>
                      <div className="text-2xl font-bold text-blue-600 mt-1">{data.total_tenants}</div>
                    </div>
                    <div className="bg-green-50 p-4 rounded">
                      <div className="text-sm text-gray-600">Active Tenants</div>
                      <div className="text-2xl font-bold text-green-600 mt-1">{data.active_tenants}</div>
                    </div>
                    <div className="bg-purple-50 p-4 rounded">
                      <div className="text-sm text-gray-600">Total Users</div>
                      <div className="text-2xl font-bold text-purple-600 mt-1">{data.total_system_users}</div>
                    </div>
                    <div className="bg-orange-50 p-4 rounded">
                      <div className="text-sm text-gray-600">Data Usage</div>
                      <div className="text-2xl font-bold text-orange-600 mt-1">{data.total_data_usage_gb}GB</div>
                    </div>
                  </div>
                </div>

                <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-6 rounded-lg">
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">System Health</h3>
                      <p className="text-sm text-gray-600 mt-1">All services operational</p>
                    </div>
                    <div className="text-right">
                      <div className="text-4xl font-bold text-green-600">{data.system_health}%</div>
                    </div>
                  </div>
                  <div className="w-full bg-blue-200 rounded-full h-3 mt-4">
                    <div
                      className="bg-green-600 h-3 rounded-full"
                      style={{
                        width: `${data.system_health}%`,
                      }}
                    ></div>
                  </div>
                </div>
              </div>
            )}

            {/* Tenants Tab */}
            {selectedTab === "tenants" && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">All Tenants ({data.total_tenants})</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">School Name</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">School Code</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Active Users</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Status</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.tenants.map((tenant) => (
                        <tr key={tenant.tenant_id} className="border-b hover:bg-gray-50">
                          <td className="py-3 px-4 text-gray-900 font-medium">{tenant.school_name}</td>
                          <td className="py-3 px-4 text-gray-700">{tenant.school_code}</td>
                          <td className="py-3 px-4 text-gray-700">{tenant.active_users}</td>
                          <td className="py-3 px-4">
                            <span
                              className={`px-3 py-1 rounded-full text-sm font-medium ${
                                tenant.status === "active"
                                  ? "bg-green-100 text-green-800"
                                  : "bg-gray-100 text-gray-800"
                              }`}
                            >
                              {tenant.status.charAt(0).toUpperCase() + tenant.status.slice(1)}
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

            {/* Metrics Tab */}
            {selectedTab === "metrics" && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">System Metrics</h3>
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-lg">
                      <div className="text-sm text-gray-600">Tenant Adoption</div>
                      <div className="mt-4">
                        <div className="flex justify-between text-sm mb-2">
                          <span>Active</span>
                          <span className="font-semibold">{data.active_tenants}</span>
                        </div>
                        <div className="w-full bg-blue-200 rounded-full h-2">
                          <div
                            className="bg-green-500 h-2 rounded-full"
                            style={{
                              width: `${(data.active_tenants / data.total_tenants) * 100}%`,
                            }}
                          ></div>
                        </div>
                        <div className="text-sm text-gray-600 mt-2">
                          {((data.active_tenants / data.total_tenants) * 100).toFixed(1)}% of {data.total_tenants}{" "}
                          tenants
                        </div>
                      </div>
                    </div>

                    <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-lg">
                      <div className="text-sm text-gray-600">Data Storage</div>
                      <div className="mt-4">
                        <div className="flex justify-between text-sm mb-2">
                          <span>Used</span>
                          <span className="font-semibold">{data.total_data_usage_gb}GB</span>
                        </div>
                        <div className="w-full bg-purple-200 rounded-full h-2">
                          <div
                            className="bg-purple-600 h-2 rounded-full"
                            style={{
                              width: `${Math.min((data.total_data_usage_gb / 1000) * 100, 100)}%`,
                            }}
                          ></div>
                        </div>
                        <div className="text-sm text-gray-600 mt-2">
                          {((data.total_data_usage_gb / 1000) * 100).toFixed(1)}% of 1TB capacity
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gradient-to-r from-green-50 to-green-100 p-6 rounded-lg">
                    <div className="text-sm text-gray-600">System Performance</div>
                    <div className="mt-4 space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-700">API Response Time</span>
                        <span className="font-semibold text-green-600">156ms avg</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-700">Database Query Time</span>
                        <span className="font-semibold text-green-600">42ms avg</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-700">Uptime</span>
                        <span className="font-semibold text-green-600">99.9%</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Settings Tab */}
            {selectedTab === "settings" && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">System Configuration</h3>
                <div className="space-y-4">
                  <div className="p-4 border rounded-lg">
                    <div className="font-semibold text-gray-900">Global Settings</div>
                    <div className="text-sm text-gray-600 mt-2">Manage platform-wide configurations</div>
                    <Button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 text-sm mt-3">
                      Configure
                    </Button>
                  </div>

                  <div className="p-4 border rounded-lg">
                    <div className="font-semibold text-gray-900">Backup & Restore</div>
                    <div className="text-sm text-gray-600 mt-2">Manage system backups and data recovery</div>
                    <Button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 text-sm mt-3">
                      Manage Backups
                    </Button>
                  </div>

                  <div className="p-4 border rounded-lg">
                    <div className="font-semibold text-gray-900">Audit Logs</div>
                    <div className="text-sm text-gray-600 mt-2">View system audit trail and activity logs</div>
                    <Button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 text-sm mt-3">
                      View Logs
                    </Button>
                  </div>

                  <div className="p-4 border rounded-lg">
                    <div className="font-semibold text-gray-900">System Maintenance</div>
                    <div className="text-sm text-gray-600 mt-2">Schedule maintenance windows and updates</div>
                    <Button className="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 text-sm mt-3">
                      Schedule Maintenance
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
  )
}
