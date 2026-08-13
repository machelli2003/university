/**
 * Section 42: Lecturer Dashboard
 * 
 * Lecturer-specific dashboard showing:
 * - Assigned courses and class details
 * - Student attendance tracking
 * - Grade submission status
 * - Assignment management
 * - Student performance metrics
 */

import React, { useState, useEffect } from "react"
import { Button } from "@/components/ui/Button"
import axios from "axios"

interface LecturerDashboardData {
  total_courses: number
  total_students: number
  avg_attendance_rate: number
  courses: any[]
  recent_grades: any[]
  attendance_alerts: any[]
  pending_assignments: number
}

export default function LecturerDashboardPage() {
  const [dashboardData, setDashboardData] = useState<LecturerDashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedTab, setSelectedTab] = useState<"overview" | "courses" | "attendance" | "grades">(
    "overview"
  )

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem("access_token")
      const response = await axios.get(
        "/api/v1/officer/dashboard/lecturer",
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
          <p className="mt-4 text-gray-600">Loading lecturer dashboard...</p>
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

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Lecturer Dashboard</h1>
              <p className="text-gray-600 mt-1">Manage courses, attendance, and grades</p>
            </div>
            <Button onClick={fetchDashboardData} className="bg-blue-600 hover:bg-blue-700">
              🔄 Refresh
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-gray-600 text-sm font-medium">Courses Assigned</p>
            <p className="text-3xl font-bold text-blue-600 mt-2">
              {dashboardData.total_courses}
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-gray-600 text-sm font-medium">Total Students</p>
            <p className="text-3xl font-bold text-green-600 mt-2">
              {dashboardData.total_students}
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-gray-600 text-sm font-medium">Avg Attendance Rate</p>
            <p className="text-3xl font-bold text-purple-600 mt-2">
              {dashboardData.avg_attendance_rate.toFixed(1)}%
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-gray-600 text-sm font-medium">Pending Assignments</p>
            <p className="text-3xl font-bold text-yellow-600 mt-2">
              {dashboardData.pending_assignments}
            </p>
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
            onClick={() => setSelectedTab("courses")}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              selectedTab === "courses"
                ? "bg-blue-600 text-white"
                : "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50"
            }`}
          >
            My Courses
          </button>
          <button
            onClick={() => setSelectedTab("attendance")}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              selectedTab === "attendance"
                ? "bg-blue-600 text-white"
                : "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50"
            }`}
          >
            Attendance
          </button>
          <button
            onClick={() => setSelectedTab("grades")}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              selectedTab === "grades"
                ? "bg-blue-600 text-white"
                : "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50"
            }`}
          >
            Grade Submission
          </button>
        </div>

        {/* Overview Tab */}
        {selectedTab === "overview" && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Assigned Courses</h2>
            <div className="space-y-3">
              {dashboardData.courses.map((course) => (
                <div key={course.course_id} className="p-4 border rounded-lg hover:bg-gray-50">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-semibold text-gray-900">{course.course_name}</div>
                      <div className="text-sm text-gray-600">{course.course_code}</div>
                      <div className="text-sm text-gray-600 mt-1">
                        {course.student_count} students enrolled
                      </div>
                    </div>
                    <Button className="bg-blue-600 hover:bg-blue-700" size="sm">
                      Manage
                    </Button>
                  </div>
                  <div className="mt-3 grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Attendance:</span>
                      <p className="font-medium text-green-600">{course.attendance_rate}%</p>
                    </div>
                    <div>
                      <span className="text-gray-600">Grades Submitted:</span>
                      <p className="font-medium text-blue-600">{course.grades_submitted}</p>
                    </div>
                    <div>
                      <span className="text-gray-600">Pending:</span>
                      <p className="font-medium text-yellow-600">{course.assignment_pending}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Courses Tab */}
        {selectedTab === "courses" && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {dashboardData.courses.map((course) => (
              <div key={course.course_id} className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-2">{course.course_name}</h3>
                <p className="text-sm text-gray-600 mb-4">{course.course_code}</p>
                <div className="space-y-2 mb-4">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Students Enrolled</span>
                    <span className="font-medium">{course.student_count}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Attendance Rate</span>
                    <span className="font-medium text-green-600">{course.attendance_rate}%</span>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button className="flex-1 bg-blue-600 hover:bg-blue-700" size="sm">
                    View Class
                  </Button>
                  <Button className="flex-1 bg-gray-600 hover:bg-gray-700" size="sm">
                    Materials
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Attendance Tab */}
        {selectedTab === "attendance" && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Class Attendance Overview</h2>
            <p className="text-gray-600 mb-6">Average attendance rate across all courses</p>
            <div className="text-center">
              <p className="text-5xl font-bold text-green-600 mb-2">
                {dashboardData.avg_attendance_rate.toFixed(1)}%
              </p>
              <p className="text-gray-600">Overall class attendance</p>
              <Button className="mt-6 bg-blue-600 hover:bg-blue-700">
                View Attendance Records
              </Button>
            </div>
          </div>
        )}

        {/* Grades Tab */}
        {selectedTab === "grades" && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Grade Submission Status</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {dashboardData.courses.map((course) => (
                <div key={course.course_id} className="p-4 border rounded-lg">
                  <p className="font-medium text-gray-900">{course.course_code}</p>
                  <p className="text-sm text-gray-600 mb-3">{course.course_name}</p>
                  <div className="mb-3">
                    <div className="flex justify-between text-sm mb-1">
                      <span>Grades Submitted</span>
                      <span className="font-medium">{course.grades_submitted}/{course.student_count}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{
                          width: `${(course.grades_submitted / course.student_count) * 100}%`,
                        }}
                      ></div>
                    </div>
                  </div>
                  <Button className="w-full bg-blue-600 hover:bg-blue-700" size="sm">
                    Submit Grades
                  </Button>
                </div>
              ))}
            </div>
            <div className="mt-6 p-4 bg-yellow-50 rounded-lg">
              <p className="text-yellow-800 font-medium">
                ⚠️ You have {dashboardData.pending_assignments} pending grade submissions
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
