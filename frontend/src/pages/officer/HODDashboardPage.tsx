import React, { useEffect, useState } from "react"
import { useAuthStore } from "@/store/authStore"
import axios from "axios"
import { Button } from "@/components/ui/Button"
import { Card } from "@/components/ui/Card"

interface CourseInfo {
  course_id: string
  course_code: string
  course_name: string
  lecturer_name: string
  enrolled_students: number
}

interface StaffInfo {
  staff_id: string
  staff_name: string
  position: string
}

interface StudentMetrics {
  level: string
  count: number
}

interface HODDashboardData {
  total_courses: number
  total_lecturers: number
  total_students: number
  avg_course_satisfaction: number
  pending_approvals: number
  courses: CourseInfo[]
  staff: StaffInfo[]
  students_by_level: StudentMetrics[]
}

export default function HODDashboardPage() {
  const { user } = useAuthStore()
  const [data, setData] = useState<HODDashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedTab, setSelectedTab] = useState<"overview" | "courses" | "staff" | "students">("overview")

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const token = localStorage.getItem("access_token")
        if (!token) return

        const response = await axios.get(`/api/v1/officer/dashboard/hod`, {
          headers: { Authorization: `Bearer ${token}` },
        })

        setData(response.data)
      } catch (error) {
        console.error("Failed to load HOD dashboard:", error)
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
          <h1 className="text-3xl font-bold text-gray-900">Head of Department Dashboard</h1>
          <p className="text-gray-600 mt-2">Welcome, {user?.first_name || "HOD"}</p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Total Courses</div>
            <div className="mt-2 text-3xl font-bold text-blue-600">{data.total_courses}</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Lecturers</div>
            <div className="mt-2 text-3xl font-bold text-green-600">{data.total_lecturers}</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Students</div>
            <div className="mt-2 text-3xl font-bold text-purple-600">{data.total_students}</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Avg Satisfaction</div>
            <div className="mt-2 text-3xl font-bold text-orange-600">{data.avg_course_satisfaction.toFixed(1)}</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Pending Approvals</div>
            <div className="mt-2 text-3xl font-bold text-red-600">{data.pending_approvals}</div>
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
              onClick={() => setSelectedTab("courses")}
              className={`px-6 py-4 font-medium ${
                selectedTab === "courses"
                  ? "border-b-2 border-blue-600 text-blue-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Courses
            </button>
            <button
              onClick={() => setSelectedTab("staff")}
              className={`px-6 py-4 font-medium ${
                selectedTab === "staff"
                  ? "border-b-2 border-blue-600 text-blue-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Staff
            </button>
            <button
              onClick={() => setSelectedTab("students")}
              className={`px-6 py-4 font-medium ${
                selectedTab === "students"
                  ? "border-b-2 border-blue-600 text-blue-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Students
            </button>
          </div>

          <div className="p-6">
            {/* Overview Tab */}
            {selectedTab === "overview" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Department Overview</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-blue-50 p-4 rounded">
                      <div className="text-sm text-gray-600">Courses Offered</div>
                      <div className="text-2xl font-bold text-blue-600 mt-1">{data.total_courses}</div>
                    </div>
                    <div className="bg-green-50 p-4 rounded">
                      <div className="text-sm text-gray-600">Faculty Members</div>
                      <div className="text-2xl font-bold text-green-600 mt-1">{data.total_lecturers}</div>
                    </div>
                    <div className="bg-purple-50 p-4 rounded">
                      <div className="text-sm text-gray-600">Enrolled Students</div>
                      <div className="text-2xl font-bold text-purple-600 mt-1">{data.total_students}</div>
                    </div>
                    <div className="bg-orange-50 p-4 rounded">
                      <div className="text-sm text-gray-600">Quality Rating</div>
                      <div className="text-2xl font-bold text-orange-600 mt-1">{data.avg_course_satisfaction.toFixed(1)}/5</div>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Students by Level</h3>
                  <div className="space-y-3">
                    {data.students_by_level.map((level) => (
                      <div key={level.level} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                        <span className="font-medium text-gray-700">Level {level.level}</span>
                        <div className="flex items-center">
                          <div className="w-32 bg-gray-200 rounded-full h-2 mr-3">
                            <div
                              className="bg-blue-600 h-2 rounded-full"
                              style={{
                                width: `${Math.min((level.count / data.total_students) * 100, 100)}%`,
                              }}
                            ></div>
                          </div>
                          <span className="text-gray-600 font-medium">{level.count}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Courses Tab */}
            {selectedTab === "courses" && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Department Courses</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Course Code</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Course Name</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Lecturer</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Students</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.courses.map((course) => (
                        <tr key={course.course_id} className="border-b hover:bg-gray-50">
                          <td className="py-3 px-4 text-gray-900">{course.course_code}</td>
                          <td className="py-3 px-4 text-gray-900">{course.course_name}</td>
                          <td className="py-3 px-4 text-gray-700">{course.lecturer_name}</td>
                          <td className="py-3 px-4 text-gray-700">{course.enrolled_students}</td>
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

            {/* Staff Tab */}
            {selectedTab === "staff" && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Department Staff</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {data.staff.map((member) => (
                    <div key={member.staff_id} className="p-4 border rounded-lg hover:shadow-md transition">
                      <div className="font-semibold text-gray-900">{member.staff_name}</div>
                      <div className="text-sm text-gray-600 mt-1">{member.position}</div>
                      <Button className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 text-sm mt-3">
                        View Profile
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Students Tab */}
            {selectedTab === "students" && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Student Distribution</h3>
                <div className="space-y-4">
                  {data.students_by_level.map((level) => (
                    <div key={level.level} className="p-4 bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg">
                      <div className="flex justify-between items-center">
                        <div>
                          <div className="font-semibold text-gray-900">Level {level.level}</div>
                          <div className="text-sm text-gray-600">Total: {level.count} students</div>
                        </div>
                        <div className="text-3xl font-bold text-blue-600">{level.count}</div>
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
