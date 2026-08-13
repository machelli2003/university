/**
 * Lecturer Grade Statistics Page
 * 
 * Shows grade distribution, statistics, and performance analytics
 * for lecturer's assigned courses.
 */

import React, { useState, useEffect, useMemo } from "react"
import axios from "axios"
import { BarChart, Bar, PieChart, Pie, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from "recharts"
import { TrendingUp, Users, Award } from "lucide-react"
import { Button } from "@/components/ui/Button"

interface Course {
  id: string
  code: string
  title: string
}

interface GradeStatistics {
  course_id: string
  course_code: string
  course_title: string
  total_students: number
  average_score: number
  highest_score: number
  lowest_score: number
  pass_rate: number
  grade_distribution: Record<string, number>
}

interface GradeData {
  grade: string
  count: number
}

const GRADE_COLORS: Record<string, string> = {
  "A": "#10b981",
  "B": "#3b82f6",
  "C": "#f59e0b",
  "D": "#ef4444",
  "F": "#991b1b",
}

export default function GradeStatisticsPage() {
  const [courses, setCourses] = useState<Course[]>([])
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null)
  const [statistics, setStatistics] = useState<GradeStatistics | null>(null)
  const [loading, setLoading] = useState(true)
  const [statsLoading, setStatsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchCourses()
  }, [])

  useEffect(() => {
    if (selectedCourse) {
      fetchGradeStatistics(selectedCourse.id)
    }
  }, [selectedCourse])

  const fetchCourses = async () => {
    try {
      setLoading(true)
      const token = localStorage.getItem("access_token")
      const response = await axios.get("/api/v1/lecturer/courses", {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true,
      })
      setCourses(response.data)
      if (response.data.length > 0) {
        setSelectedCourse(response.data[0])
      }
    } catch (err) {
      setError("Failed to load courses")
    } finally {
      setLoading(false)
    }
  }

  const fetchGradeStatistics = async (courseId: string) => {
    try {
      setStatsLoading(true)
      const token = localStorage.getItem("access_token")
      const response = await axios.get(`/api/v1/lecturer/courses/${courseId}/grade-statistics`, {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true,
      })
      setStatistics(response.data)
    } catch (err) {
      setError("Failed to load grade statistics")
    } finally {
      setStatsLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading grade statistics...</p>
        </div>
      </div>
    )
  }

  if (error && !statistics) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-700">{error}</p>
            <Button onClick={fetchCourses} className="mt-4">
              Retry
            </Button>
          </div>
        </div>
      </div>
    )
  }

  // PERFORMANCE OPTIMIZATION: Memoize chart data to prevent unnecessary recalculations
  const gradeDistributionData: GradeData[] = useMemo(() => {
    if (!statistics) return []
    return Object.entries(statistics.grade_distribution).map(([grade, count]) => ({
      grade,
      count,
    }))
  }, [statistics])

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">Grade Statistics</h1>
          <p className="text-gray-600 mt-1">View grade distribution and performance analytics</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* Course Selection */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <label className="block text-sm font-medium text-gray-900 mb-2">Select Course</label>
          <select
            value={selectedCourse?.id || ""}
            onChange={(e) => {
              const course = courses.find((c) => c.id === e.target.value)
              setSelectedCourse(course || null)
            }}
            className="w-full md:w-96 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
          >
            {courses.map((course) => (
              <option key={course.id} value={course.id}>
                {course.code} - {course.title}
              </option>
            ))}
          </select>
        </div>

        {statsLoading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Loading statistics...</p>
          </div>
        ) : statistics ? (
          <>
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
              <MetricBox
                label="Total Students"
                value={statistics.total_students}
                icon={Users}
                color="blue"
              />
              <MetricBox
                label="Average Score"
                value={statistics.average_score.toFixed(2)}
                suffix="/100"
                icon={TrendingUp}
                color="green"
              />
              <MetricBox
                label="Highest Score"
                value={statistics.highest_score}
                suffix="/100"
                icon={Award}
                color="green"
              />
              <MetricBox
                label="Lowest Score"
                value={statistics.lowest_score}
                suffix="/100"
                icon={TrendingUp}
                color="red"
              />
              <MetricBox
                label="Pass Rate"
                value={statistics.pass_rate.toFixed(1)}
                suffix="%"
                icon={Award}
                color="green"
              />
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
              {/* Grade Distribution Pie Chart */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Grade Distribution</h2>
                {gradeDistributionData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={gradeDistributionData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={(entry: any) => `${entry.grade}: ${entry.count}`}
                        outerRadius={100}
                        fill="#8884d8"
                        dataKey="count"
                      >
                        {gradeDistributionData.map((entry) => (
                          <Cell key={`cell-${entry.grade}`} fill={GRADE_COLORS[entry.grade] || "#6b7280"} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => `${value} students`} />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <p className="text-center text-gray-500 py-8">No grade data available</p>
                )}
              </div>

              {/* Grade Count Bar Chart */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Students per Grade</h2>
                {gradeDistributionData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart
                      data={gradeDistributionData}
                      margin={{ top: 20, right: 30, left: 0, bottom: 20 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                      <XAxis dataKey="grade" stroke="#6b7280" />
                      <YAxis stroke="#6b7280" />
                      <Tooltip formatter={(value) => `${value} students`} />
                      <Bar dataKey="count" fill="#3b82f6" radius={[8, 8, 0, 0]}>
                        {gradeDistributionData.map((entry) => (
                          <Cell key={`cell-${entry.grade}`} fill={GRADE_COLORS[entry.grade] || "#6b7280"} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <p className="text-center text-gray-500 py-8">No grade data available</p>
                )}
              </div>
            </div>

            {/* Grade Legend */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-lg font-bold text-gray-900 mb-4">Grading Scale</h2>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {["A", "B", "C", "D", "F"].map((grade) => (
                  <div key={grade} className="flex items-center gap-3">
                    <div
                      className="w-4 h-4 rounded"
                      style={{ backgroundColor: GRADE_COLORS[grade] }}
                    ></div>
                    <div>
                      <p className="font-semibold text-gray-900">{grade}</p>
                      <p className="text-xs text-gray-600">
                        {grade === "A" && "80-100"}
                        {grade === "B" && "70-79"}
                        {grade === "C" && "60-69"}
                        {grade === "D" && "50-59"}
                        {grade === "F" && "<50"}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Performance Insights */}
            <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h2 className="text-lg font-bold text-blue-900 mb-4">📊 Performance Insights</h2>
              <ul className="space-y-2 text-blue-800">
                {statistics.average_score >= 75 && (
                  <li>✓ Overall class performance is excellent with an average score of {statistics.average_score.toFixed(1)}</li>
                )}
                {statistics.average_score < 75 && statistics.average_score >= 60 && (
                  <li>ℹ Average score of {statistics.average_score.toFixed(1)} suggests room for improvement</li>
                )}
                {statistics.average_score < 60 && (
                  <li>⚠ Average score of {statistics.average_score.toFixed(1)} is below 60. Consider reviewing teaching strategies</li>
                )}
                {statistics.pass_rate >= 85 && (
                  <li>✓ Pass rate of {statistics.pass_rate.toFixed(1)}% is excellent</li>
                )}
                {statistics.pass_rate < 85 && statistics.pass_rate >= 70 && (
                  <li>ℹ Pass rate of {statistics.pass_rate.toFixed(1)}% - consider additional support for struggling students</li>
                )}
                {statistics.pass_rate < 70 && (
                  <li>⚠ Pass rate of {statistics.pass_rate.toFixed(1)}% is concerning - intervention may be needed</li>
                )}
              </ul>
            </div>
          </>
        ) : null}
      </div>
    </div>
  )
}

interface MetricBoxProps {
  label: string
  value: string | number
  suffix?: string
  icon: React.ComponentType<{ className?: string }>
  color: "blue" | "green" | "red"
}

function MetricBox({ label, value, suffix, icon: Icon, color }: MetricBoxProps) {
  const colorClasses = {
    blue: "bg-blue-50 border-blue-200 text-blue-900",
    green: "bg-green-50 border-green-200 text-green-900",
    red: "bg-red-50 border-red-200 text-red-900",
  }

  const iconColorClasses = {
    blue: "text-blue-600",
    green: "text-green-600",
    red: "text-red-600",
  }

  return (
    <div className={`rounded-lg border p-4 ${colorClasses[color]}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium">{label}</p>
          <p className="text-2xl font-bold mt-1">
            {value}
            {suffix && <span className="text-lg">{suffix}</span>}
          </p>
        </div>
        <Icon className={`w-8 h-8 ${iconColorClasses[color]} opacity-50`} />
      </div>
    </div>
  )
}
