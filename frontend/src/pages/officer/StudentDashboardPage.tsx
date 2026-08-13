import React, { useEffect, useState } from "react"
import { useAuthStore } from "@/store/authStore"
import axios from "axios"
import { Button } from "@/components/ui/Button"
import { Card } from "@/components/ui/Card"

interface CourseEnrolled {
  course_code: string
  course_name: string
  lecturer_name: string
  credits: number
  grade: string
}

interface StudentDashboardData {
  student_level: string
  enrolled_courses: number
  current_gpa: number
  academic_standing: string
  next_important_date: string
  courses: CourseEnrolled[]
  transcript: Array<{
    course_code: string
    grade: string
  }>
}

export default function StudentDashboardPage() {
  const { user } = useAuthStore()
  const [data, setData] = useState<StudentDashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedTab, setSelectedTab] = useState<"overview" | "courses" | "progress" | "transcript">("overview")

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const token = localStorage.getItem("access_token")
        if (!token) return

        const response = await axios.get(`/api/v1/officer/dashboard/student`, {
          headers: { Authorization: `Bearer ${token}` },
        })

        setData(response.data)
      } catch (error) {
        console.error("Failed to load Student dashboard:", error)
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

  const standingColor =
    data.academic_standing === "good"
      ? "text-green-600"
      : data.academic_standing === "warning"
        ? "text-yellow-600"
        : "text-red-600"

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Student Dashboard</h1>
          <p className="text-gray-600 mt-2">Welcome back, {user?.first_name || "Student"}</p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Current Level</div>
            <div className="mt-2 text-3xl font-bold text-blue-600">{data.student_level}</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Enrolled Courses</div>
            <div className="mt-2 text-3xl font-bold text-green-600">{data.enrolled_courses}</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Current GPA</div>
            <div className="mt-2 text-3xl font-bold text-purple-600">{data.current_gpa.toFixed(2)}</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Academic Standing</div>
            <div className={`mt-2 text-3xl font-bold ${standingColor}`}>
              {data.academic_standing.charAt(0).toUpperCase() + data.academic_standing.slice(1)}
            </div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Next Important Date</div>
            <div className="mt-2 text-sm font-bold text-orange-600">{data.next_important_date}</div>
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
              My Courses
            </button>
            <button
              onClick={() => setSelectedTab("progress")}
              className={`px-6 py-4 font-medium ${
                selectedTab === "progress"
                  ? "border-b-2 border-blue-600 text-blue-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Progress
            </button>
            <button
              onClick={() => setSelectedTab("transcript")}
              className={`px-6 py-4 font-medium ${
                selectedTab === "transcript"
                  ? "border-b-2 border-blue-600 text-blue-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Transcript
            </button>
          </div>

          <div className="p-6">
            {/* Overview Tab */}
            {selectedTab === "overview" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Academic Overview</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-lg">
                      <div className="text-sm text-gray-600">Current Level</div>
                      <div className="text-3xl font-bold text-blue-600 mt-2">{data.student_level}</div>
                      <p className="text-sm text-gray-600 mt-2">{data.enrolled_courses} courses enrolled</p>
                    </div>

                    <div className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-lg">
                      <div className="text-sm text-gray-600">GPA</div>
                      <div className="text-3xl font-bold text-green-600 mt-2">{data.current_gpa.toFixed(2)}/4.0</div>
                      <p className="text-sm text-gray-600 mt-2">Cumulative</p>
                    </div>

                    <div className={`bg-gradient-to-br ${
                      data.academic_standing === "good"
                        ? "from-emerald-50 to-emerald-100"
                        : data.academic_standing === "warning"
                          ? "from-yellow-50 to-yellow-100"
                          : "from-red-50 to-red-100"
                    } p-6 rounded-lg`}>
                      <div className="text-sm text-gray-600">Academic Standing</div>
                      <div className={`text-2xl font-bold mt-2 ${standingColor}`}>
                        {data.academic_standing.charAt(0).toUpperCase() + data.academic_standing.slice(1)}
                      </div>
                      <p className="text-sm text-gray-600 mt-2">Status is good</p>
                    </div>
                  </div>
                </div>

                <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded">
                  <div className="text-sm font-semibold text-gray-900">Next Important Date</div>
                  <div className="text-lg text-yellow-700 mt-1 font-bold">{data.next_important_date}</div>
                </div>
              </div>
            )}

            {/* Courses Tab */}
            {selectedTab === "courses" && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Enrolled Courses ({data.enrolled_courses})</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Course Code</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Course Name</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Lecturer</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Credits</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Grade</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.courses.map((course) => (
                        <tr key={course.course_code} className="border-b hover:bg-gray-50">
                          <td className="py-3 px-4 text-gray-900 font-medium">{course.course_code}</td>
                          <td className="py-3 px-4 text-gray-700">{course.course_name}</td>
                          <td className="py-3 px-4 text-gray-700">{course.lecturer_name}</td>
                          <td className="py-3 px-4 text-gray-700">{course.credits} credits</td>
                          <td className="py-3 px-4">
                            <span className="px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                              {course.grade || "TBA"}
                            </span>
                          </td>
                          <td className="py-3 px-4">
                            <Button className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 text-sm">
                              Details
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Progress Tab */}
            {selectedTab === "progress" && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Academic Progress</h3>
                <div className="space-y-6">
                  <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-6 rounded-lg">
                    <div className="text-sm text-gray-600">GPA Progress</div>
                    <div className="mt-4">
                      <div className="flex items-end justify-between mb-2">
                        <span className="text-gray-600">Target: 3.5</span>
                        <span className="text-2xl font-bold text-blue-600">{data.current_gpa.toFixed(2)}</span>
                      </div>
                      <div className="w-full bg-blue-200 rounded-full h-3">
                        <div
                          className="bg-green-500 h-3 rounded-full"
                          style={{
                            width: `${Math.min((data.current_gpa / 4.0) * 100, 100)}%`,
                          }}
                        ></div>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-semibold text-gray-900 mb-3">Course Performance Summary</h4>
                    <div className="space-y-2">
                      {data.courses.slice(0, 5).map((course) => (
                        <div key={course.course_code} className="p-3 bg-gray-50 rounded flex justify-between">
                          <span className="text-gray-700">{course.course_name}</span>
                          <span className="font-semibold text-gray-900">{course.grade || "In Progress"}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Transcript Tab */}
            {selectedTab === "transcript" && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Academic Transcript</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Course Code</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Grade</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.transcript.map((record) => (
                        <tr key={record.course_code} className="border-b hover:bg-gray-50">
                          <td className="py-3 px-4 text-gray-900 font-medium">{record.course_code}</td>
                          <td className="py-3 px-4">
                            <span className="px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                              {record.grade}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
