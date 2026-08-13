import React, { useEffect, useState } from "react"
import { useAuthStore } from "@/store/authStore"
import axios from "axios"
import { Button } from "@/components/ui/Button"
import { Card } from "@/components/ui/Card"

interface ExamInfo {
  exam_id: string
  course_code: string
  course_name: string
  exam_date: string
  status: "scheduled" | "completed" | "pending"
}

interface ResultInfo {
  result_id: string
  course_code: string
  verified: boolean
  verified_date: string | null
}

interface ExamDashboardData {
  total_exams: number
  scheduled_exams: number
  completed_exams: number
  pending_results: number
  verification_rate: number
  exams: ExamInfo[]
  results_verification: ResultInfo[]
}

export default function ExamOfficerDashboardPage() {
  const { user } = useAuthStore()
  const [data, setData] = useState<ExamDashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedTab, setSelectedTab] = useState<"overview" | "exams" | "results" | "verification">("overview")

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const token = localStorage.getItem("access_token")
        if (!token) return

        const response = await axios.get(`/api/v1/officer/dashboard/exam`, {
          headers: { Authorization: `Bearer ${token}` },
        })

        setData(response.data)
      } catch (error) {
        console.error("Failed to load Exam dashboard:", error)
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
          <h1 className="text-3xl font-bold text-gray-900">Examination Officer Dashboard</h1>
          <p className="text-gray-600 mt-2">Welcome, {user?.first_name || "Exam Officer"}</p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Total Exams</div>
            <div className="mt-2 text-3xl font-bold text-blue-600">{data.total_exams}</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Scheduled</div>
            <div className="mt-2 text-3xl font-bold text-green-600">{data.scheduled_exams}</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Completed</div>
            <div className="mt-2 text-3xl font-bold text-purple-600">{data.completed_exams}</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Pending Results</div>
            <div className="mt-2 text-3xl font-bold text-orange-600">{data.pending_results}</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Verification Rate</div>
            <div className="mt-2 text-3xl font-bold text-red-600">{data.verification_rate.toFixed(1)}%</div>
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
              onClick={() => setSelectedTab("exams")}
              className={`px-6 py-4 font-medium ${
                selectedTab === "exams"
                  ? "border-b-2 border-blue-600 text-blue-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Exams
            </button>
            <button
              onClick={() => setSelectedTab("results")}
              className={`px-6 py-4 font-medium ${
                selectedTab === "results"
                  ? "border-b-2 border-blue-600 text-blue-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Results
            </button>
            <button
              onClick={() => setSelectedTab("verification")}
              className={`px-6 py-4 font-medium ${
                selectedTab === "verification"
                  ? "border-b-2 border-blue-600 text-blue-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Verification
            </button>
          </div>

          <div className="p-6">
            {/* Overview Tab */}
            {selectedTab === "overview" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Examination System Status</h3>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="bg-blue-50 p-4 rounded">
                      <div className="text-sm text-gray-600">Total Exams</div>
                      <div className="text-2xl font-bold text-blue-600 mt-1">{data.total_exams}</div>
                    </div>
                    <div className="bg-green-50 p-4 rounded">
                      <div className="text-sm text-gray-600">Scheduled</div>
                      <div className="text-2xl font-bold text-green-600 mt-1">{data.scheduled_exams}</div>
                    </div>
                    <div className="bg-purple-50 p-4 rounded">
                      <div className="text-sm text-gray-600">Completed</div>
                      <div className="text-2xl font-bold text-purple-600 mt-1">{data.completed_exams}</div>
                    </div>
                    <div className="bg-orange-50 p-4 rounded">
                      <div className="text-sm text-gray-600">Pending</div>
                      <div className="text-2xl font-bold text-orange-600 mt-1">{data.pending_results}</div>
                    </div>
                  </div>
                </div>

                <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-6 rounded-lg">
                  <h3 className="text-lg font-semibold text-gray-900">Result Verification Progress</h3>
                  <div className="mt-4 flex items-end gap-4">
                    <div className="flex-1">
                      <div className="w-full bg-blue-200 rounded-full h-3">
                        <div
                          className="bg-blue-600 h-3 rounded-full"
                          style={{
                            width: `${data.verification_rate}%`,
                          }}
                        ></div>
                      </div>
                    </div>
                    <div className="text-3xl font-bold text-blue-600">{data.verification_rate.toFixed(1)}%</div>
                  </div>
                </div>
              </div>
            )}

            {/* Exams Tab */}
            {selectedTab === "exams" && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Scheduled Exams</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Course Code</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Course Name</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Date</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Status</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.exams.map((exam) => (
                        <tr key={exam.exam_id} className="border-b hover:bg-gray-50">
                          <td className="py-3 px-4 text-gray-900">{exam.course_code}</td>
                          <td className="py-3 px-4 text-gray-700">{exam.course_name}</td>
                          <td className="py-3 px-4 text-gray-700">{exam.exam_date}</td>
                          <td className="py-3 px-4">
                            <span
                              className={`px-3 py-1 rounded-full text-sm font-medium ${
                                exam.status === "completed"
                                  ? "bg-green-100 text-green-800"
                                  : exam.status === "scheduled"
                                    ? "bg-blue-100 text-blue-800"
                                    : "bg-yellow-100 text-yellow-800"
                              }`}
                            >
                              {exam.status.charAt(0).toUpperCase() + exam.status.slice(1)}
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

            {/* Results Tab */}
            {selectedTab === "results" && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Exam Results</h3>
                <div className="space-y-3">
                  {data.results_verification.map((result) => (
                    <div key={result.result_id} className="p-4 border rounded-lg hover:shadow-md transition">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-semibold text-gray-900">{result.course_code}</div>
                          <div className="text-sm text-gray-600">
                            {result.verified ? `Verified on ${result.verified_date}` : "Awaiting verification"}
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {result.verified ? (
                            <span className="px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                              Verified
                            </span>
                          ) : (
                            <span className="px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800">
                              Pending
                            </span>
                          )}
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

            {/* Verification Tab */}
            {selectedTab === "verification" && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Verification Report</h3>
                <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-6 rounded-lg">
                  <div className="grid grid-cols-2 gap-4 mb-6">
                    <div>
                      <div className="text-sm text-gray-600">Verified Results</div>
                      <div className="text-3xl font-bold text-green-600 mt-2">
                        {Math.round((data.verification_rate / 100) * data.pending_results)}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600">Pending Verification</div>
                      <div className="text-3xl font-bold text-orange-600 mt-2">
                        {data.pending_results -
                          Math.round((data.verification_rate / 100) * data.pending_results)}
                      </div>
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600 mb-2">Overall Verification Progress</div>
                    <div className="w-full bg-blue-200 rounded-full h-3">
                      <div
                        className="bg-green-600 h-3 rounded-full"
                        style={{
                          width: `${data.verification_rate}%`,
                        }}
                      ></div>
                    </div>
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
