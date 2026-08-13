import React, { useEffect, useState } from "react"
import { useAuthStore } from "@/store/authStore"
import axios from "axios"
import { Button } from "@/components/ui/Button"
import { Card } from "@/components/ui/Card"

interface ProgrammeInfo {
  programme_id: string
  programme_code: string
  programme_name: string
  enrolled_students: number
}

interface DepartmentInfo {
  department_id: string
  department_name: string
  hod_name: string
  student_count: number
}

interface DeanDashboardData {
  total_departments: number
  total_programmes: number
  total_students: number
  total_staff: number
  pending_decisions: number
  departments: DepartmentInfo[]
  programmes: ProgrammeInfo[]
  department_performance: Array<{
    department_name: string
    avg_gpa: number
  }>
}

export default function DeanDashboardPage() {
  const { user } = useAuthStore()
  const [data, setData] = useState<DeanDashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedTab, setSelectedTab] = useState<"overview" | "departments" | "programmes" | "performance">("overview")

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const token = localStorage.getItem("access_token")
        if (!token) return

        const response = await axios.get(`/api/v1/officer/dashboard/dean`, {
          headers: { Authorization: `Bearer ${token}` },
        })

        setData(response.data)
      } catch (error) {
        console.error("Failed to load Dean dashboard:", error)
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
          <h1 className="text-3xl font-bold text-gray-900">Dean of Faculty Dashboard</h1>
          <p className="text-gray-600 mt-2">Welcome, {user?.first_name || "Dean"}</p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Departments</div>
            <div className="mt-2 text-3xl font-bold text-blue-600">{data.total_departments}</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Programmes</div>
            <div className="mt-2 text-3xl font-bold text-green-600">{data.total_programmes}</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Students</div>
            <div className="mt-2 text-3xl font-bold text-purple-600">{data.total_students}</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Staff</div>
            <div className="mt-2 text-3xl font-bold text-orange-600">{data.total_staff}</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Pending Decisions</div>
            <div className="mt-2 text-3xl font-bold text-red-600">{data.pending_decisions}</div>
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
              onClick={() => setSelectedTab("departments")}
              className={`px-6 py-4 font-medium ${
                selectedTab === "departments"
                  ? "border-b-2 border-blue-600 text-blue-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Departments
            </button>
            <button
              onClick={() => setSelectedTab("programmes")}
              className={`px-6 py-4 font-medium ${
                selectedTab === "programmes"
                  ? "border-b-2 border-blue-600 text-blue-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Programmes
            </button>
            <button
              onClick={() => setSelectedTab("performance")}
              className={`px-6 py-4 font-medium ${
                selectedTab === "performance"
                  ? "border-b-2 border-blue-600 text-blue-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Performance
            </button>
          </div>

          <div className="p-6">
            {/* Overview Tab */}
            {selectedTab === "overview" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Faculty Overview</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-blue-50 p-4 rounded">
                      <div className="text-sm text-gray-600">Departments</div>
                      <div className="text-2xl font-bold text-blue-600 mt-1">{data.total_departments}</div>
                    </div>
                    <div className="bg-green-50 p-4 rounded">
                      <div className="text-sm text-gray-600">Programmes</div>
                      <div className="text-2xl font-bold text-green-600 mt-1">{data.total_programmes}</div>
                    </div>
                    <div className="bg-purple-50 p-4 rounded">
                      <div className="text-sm text-gray-600">Students</div>
                      <div className="text-2xl font-bold text-purple-600 mt-1">{data.total_students}</div>
                    </div>
                    <div className="bg-orange-50 p-4 rounded">
                      <div className="text-sm text-gray-600">Total Staff</div>
                      <div className="text-2xl font-bold text-orange-600 mt-1">{data.total_staff}</div>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 p-6 rounded-lg">
                    <div className="text-lg font-semibold text-gray-900">Pending Decisions</div>
                    <div className="text-4xl font-bold text-yellow-600 mt-3">{data.pending_decisions}</div>
                    <p className="text-sm text-gray-600 mt-2">Awaiting your review</p>
                  </div>

                  <div className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-lg">
                    <div className="text-lg font-semibold text-gray-900">Faculty Status</div>
                    <div className="text-sm text-gray-600 mt-3">
                      <div className="flex justify-between py-1">
                        <span>Active Departments:</span>
                        <span className="font-semibold">{data.total_departments}</span>
                      </div>
                      <div className="flex justify-between py-1">
                        <span>Active Programmes:</span>
                        <span className="font-semibold">{data.total_programmes}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Departments Tab */}
            {selectedTab === "departments" && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Faculty Departments</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Department Name</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">HOD</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Students</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.departments.map((dept) => (
                        <tr key={dept.department_id} className="border-b hover:bg-gray-50">
                          <td className="py-3 px-4 font-medium text-gray-900">{dept.department_name}</td>
                          <td className="py-3 px-4 text-gray-700">{dept.hod_name}</td>
                          <td className="py-3 px-4 text-gray-700">{dept.student_count}</td>
                          <td className="py-3 px-4">
                            <Button className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 text-sm">
                              View Details
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Programmes Tab */}
            {selectedTab === "programmes" && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Faculty Programmes</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {data.programmes.map((prog) => (
                    <div key={prog.programme_id} className="p-4 border rounded-lg hover:shadow-lg transition">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="font-semibold text-gray-900">{prog.programme_name}</div>
                          <div className="text-sm text-gray-600 mt-1">Code: {prog.programme_code}</div>
                          <div className="text-sm text-gray-600">Enrolled: {prog.enrolled_students} students</div>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-blue-600">{prog.enrolled_students}</div>
                        </div>
                      </div>
                      <Button className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 text-sm mt-3 w-full">
                        View Programme
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Performance Tab */}
            {selectedTab === "performance" && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Department Performance (Avg GPA)</h3>
                <div className="space-y-4">
                  {data.department_performance.map((dept) => (
                    <div key={dept.department_name} className="p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div className="font-medium text-gray-900">{dept.department_name}</div>
                        <div className="flex items-center">
                          <div className="w-48 bg-gray-300 rounded-full h-3 mr-4">
                            <div
                              className="bg-green-500 h-3 rounded-full"
                              style={{
                                width: `${Math.min((dept.avg_gpa / 4.0) * 100, 100)}%`,
                              }}
                            ></div>
                          </div>
                          <span className="text-lg font-bold text-gray-900 w-12 text-right">
                            {dept.avg_gpa.toFixed(2)}
                          </span>
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
