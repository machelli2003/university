/**
 * Section 41: Registrar Dashboard
 * 
 * Registrar-specific dashboard showing:
 * - Student enrollment statistics with charts
 * - Academic standing distribution
 * - Recent enrollments
 * - Student progression
 * - Graduation eligibility
 * - Enhanced UI with Recharts visualizations
 */

import React, { useState, useEffect } from "react"
import { Button } from "@/components/ui/Button"
import axios from "axios"
import {
  PieChart,
  Pie,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from "recharts"
import { TrendingUp, Users, Award, AlertCircle } from "lucide-react"

interface RegistrarDashboardData {
  enrollment_stats: {
    total_enrolled: number
    enrolled_this_month: number
    pending_enrollment: number
    verified_enrollment: number
    unverified_enrollment: number
  }
  students_by_academic_standing: Record<string, number>
  students_by_level: Record<string, number>
  recent_enrollments: any[]
  pending_enrollment_verification: any[]
  students_on_probation: any[]
  graduation_eligible: any[]
  monthly_enrollment_rate: number
  verification_completion_rate: number
}

export default function RegistrarDashboardPage() {
  const [dashboardData, setDashboardData] = useState<RegistrarDashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedTab, setSelectedTab] = useState<"overview" | "students" | "academic" | "progression">(
    "overview"
  )

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem("access_token")
      const response = await axios.get(
        "/api/v1/officer/dashboard/registrar",
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
          <p className="mt-4 text-gray-600">Loading registrar dashboard...</p>
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

  const { enrollment_stats, students_by_academic_standing, students_by_level } = dashboardData

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Registrar Dashboard</h1>
              <p className="text-gray-600 mt-1">Manage student enrollments and academic records</p>
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
            <p className="text-gray-600 text-sm font-medium">Total Enrolled</p>
            <p className="text-3xl font-bold text-green-600 mt-2">
              {enrollment_stats.total_enrolled}
            </p>
            <p className="text-xs text-gray-500 mt-1">Students</p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-gray-600 text-sm font-medium">Enrolled This Month</p>
            <p className="text-3xl font-bold text-blue-600 mt-2">
              {enrollment_stats.enrolled_this_month}
            </p>
            <p className="text-xs text-gray-500 mt-1">New students</p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-gray-600 text-sm font-medium">Pending Enrollment</p>
            <p className="text-3xl font-bold text-yellow-600 mt-2">
              {enrollment_stats.pending_enrollment}
            </p>
            <p className="text-xs text-gray-500 mt-1">Verification pending</p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-gray-600 text-sm font-medium">Academic Good Standing</p>
            <p className="text-3xl font-bold text-green-600 mt-2">
              {students_by_academic_standing["good"] || 0}
            </p>
            <p className="text-xs text-gray-500 mt-1">Status: good</p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-gray-600 text-sm font-medium">On Probation</p>
            <p className="text-3xl font-bold text-red-600 mt-2">
              {students_by_academic_standing["probation"] || 0}
            </p>
            <p className="text-xs text-gray-500 mt-1">Academic warning</p>
          </div>
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-gray-900 font-semibold mb-2">📈 Monthly Enrollment Rate</p>
            <p className="text-4xl font-bold text-blue-600">
              {dashboardData.monthly_enrollment_rate.toFixed(1)}%
            </p>
            <p className="text-gray-600 text-sm mt-2">Enrolled this month vs total</p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-gray-900 font-semibold mb-2">✅ Verification Rate</p>
            <p className="text-4xl font-bold text-green-600">
              {dashboardData.verification_completion_rate.toFixed(1)}%
            </p>
            <p className="text-gray-600 text-sm mt-2">Enrollment verifications complete</p>
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
            onClick={() => setSelectedTab("students")}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              selectedTab === "students"
                ? "bg-blue-600 text-white"
                : "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50"
            }`}
          >
            Students by Level
          </button>
          <button
            onClick={() => setSelectedTab("academic")}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              selectedTab === "academic"
                ? "bg-blue-600 text-white"
                : "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50"
            }`}
          >
            Academic Standing
          </button>
          <button
            onClick={() => setSelectedTab("progression")}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              selectedTab === "progression"
                ? "bg-blue-600 text-white"
                : "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50"
            }`}
          >
            Recent Enrollments
          </button>
        </div>

        {/* Overview Tab - Enhanced with Charts */}
        {selectedTab === "overview" && (
          <div className="space-y-6">
            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Academic Standing Pie Chart */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <Award className="w-5 h-5 text-blue-600" />
                  Academic Standing Distribution
                </h2>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={getPieChartData(students_by_academic_standing)}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={renderCustomLabel}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {STANDING_COLORS.map((entry) => (
                        <Cell key={`cell-${entry.name}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip 
                      formatter={(value) => `${value} students`}
                      contentStyle={{ backgroundColor: "#fff", border: "1px solid #ccc" }}
                    />
                  </PieChart>
                </ResponsiveContainer>
                <div className="mt-4 grid grid-cols-1 gap-2">
                  {Object.entries(students_by_academic_standing).map(([key, value]) => (
                    <div key={key} className="flex justify-between items-center">
                      <div className="flex items-center gap-2">
                        <div 
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: getColorForStanding(key) }}
                        ></div>
                        <span className="text-sm text-gray-700 capitalize">{formatStandingLabel(key)}</span>
                      </div>
                      <span className="text-sm font-semibold text-gray-900">{value}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Student Level Distribution Bar Chart */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <Users className="w-5 h-5 text-green-600" />
                  Students by Academic Level
                </h2>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart
                    data={getBarChartData(students_by_level)}
                    margin={{ top: 20, right: 30, left: 0, bottom: 20 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis dataKey="name" stroke="#6b7280" />
                    <YAxis stroke="#6b7280" />
                    <Tooltip 
                      contentStyle={{ backgroundColor: "#fff", border: "1px solid #ccc" }}
                      formatter={(value) => `${value} students`}
                    />
                    <Bar dataKey="value" fill="#10b981" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Key Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <MetricCard 
                title="Good Standing"
                value={students_by_academic_standing["good"] || 0}
                icon={Award}
                color="green"
                trend="+5%"
              />
              <MetricCard 
                title="On Warning"
                value={students_by_academic_standing["warning"] || 0}
                icon={AlertCircle}
                color="yellow"
                trend="-2%"
              />
              <MetricCard 
                title="On Probation"
                value={students_by_academic_standing["probation"] || 0}
                icon={TrendingUp}
                color="red"
                trend="+1%"
              />
              <MetricCard 
                title="Graduation Ready"
                value={dashboardData.graduation_eligible?.length || 0}
                icon={Award}
                color="blue"
                trend="+3%"
              />
            </div>
          </div>
        )}

        {/* Students by Level Tab */}
        {selectedTab === "students" && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Student Distribution by Academic Level</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {["100", "200", "300", "400"].map((level) => (
                <div key={level} className="p-4 border rounded-lg text-center">
                  <p className="text-gray-600 font-medium">Level {level}</p>
                  <p className="text-4xl font-bold text-blue-600 mt-2">
                    {students_by_level[level] || 0}
                  </p>
                  <p className="text-sm text-gray-500 mt-2">
                    {(
                      ((students_by_level[level] || 0) /
                        enrollment_stats.total_enrolled) *
                      100
                    ).toFixed(1)}
                    % of total
                  </p>
                  <Button className="w-full mt-4 bg-blue-600 hover:bg-blue-700" size="sm">
                    View Level {level} Students
                  </Button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Academic Standing Tab */}
        {selectedTab === "academic" && (
          <div className="space-y-6">
            {/* Good Standing */}
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <h3 className="text-lg font-bold text-green-900 mb-3">
                ✅ Academic Good Standing ({students_by_academic_standing["good"] || 0})
              </h3>
              <p className="text-green-800 mb-4">
                Students meeting all academic requirements and making satisfactory progress.
              </p>
              <Button className="bg-green-600 hover:bg-green-700">View All</Button>
            </div>

            {/* Academic Warning */}
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
              <h3 className="text-lg font-bold text-yellow-900 mb-3">
                ⚠️ Academic Warning ({students_by_academic_standing["warning"] || 0})
              </h3>
              <p className="text-yellow-800 mb-4">
                Students with declining grades or attendance issues. Intervention recommended.
              </p>
              <Button className="bg-yellow-600 hover:bg-yellow-700">View All & Intervene</Button>
            </div>

            {/* Probation */}
            <div className="bg-red-50 border border-red-200 rounded-lg p-6">
              <h3 className="text-lg font-bold text-red-900 mb-3">
                🚨 On Academic Probation ({students_by_academic_standing["probation"] || 0})
              </h3>
              <p className="text-red-800 mb-4">
                Students at risk of academic dismissal. Close monitoring required.
              </p>
              <Button className="bg-red-600 hover:bg-red-700">Review & Plan Intervention</Button>
            </div>
          </div>
        )}

        {/* Recent Enrollments Tab */}
        {selectedTab === "progression" && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Student Enrollments</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left font-medium text-gray-900">Student Name</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-900">Student ID</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-900">Programme</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-900">Enrolled Date</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-900">Standing</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-900">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {dashboardData.recent_enrollments.map((student) => (
                    <tr key={student.applicant_id} className="border-t hover:bg-gray-50">
                      <td className="px-4 py-3 font-medium text-gray-900">{student.full_name}</td>
                      <td className="px-4 py-3 text-gray-600">{student.student_id}</td>
                      <td className="px-4 py-3 text-gray-600">{student.programme}</td>
                      <td className="px-4 py-3 text-gray-600">
                        {new Date(student.enrolled_date).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-3">
                        <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">
                          {student.academic_standing}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
                          View Record
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {dashboardData.recent_enrollments.length === 0 && (
                <div className="p-6 text-center text-gray-600">No recent enrollments</div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// Helper functions and constants
const STANDING_COLORS = [
  { name: "Excellent", color: "#10b981" },
  { name: "Good", color: "#3b82f6" },
  { name: "Satisfactory", color: "#f59e0b" },
  { name: "Warning", color: "#ef4444" },
  { name: "Probation", color: "#dc2626" },
  { name: "At-Risk", color: "#991b1b" },
  { name: "Suspended", color: "#000000" },
]

function getPieChartData(standingData: Record<string, number>) {
  return Object.entries(standingData).map(([key, value]) => ({
    name: formatStandingLabel(key),
    value: value,
  }))
}

function getBarChartData(levelData: Record<string, number>) {
  return ["100", "200", "300", "400"].map((level) => ({
    name: `Level ${level}`,
    value: levelData[level] || 0,
  }))
}

function getColorForStanding(key: string): string {
  const colorMap: Record<string, string> = {
    excellent: "#10b981",
    good: "#3b82f6",
    satisfactory: "#f59e0b",
    warning: "#ef4444",
    probation: "#dc2626",
    at_risk: "#991b1b",
    suspended: "#000000",
  }
  return colorMap[key] || "#6b7280"
}

function formatStandingLabel(key: string): string {
  const labelMap: Record<string, string> = {
    excellent: "Excellent",
    good: "Good",
    satisfactory: "Satisfactory",
    warning: "Warning",
    probation: "Probation",
    at_risk: "At-Risk",
    suspended: "Suspended",
  }
  return labelMap[key] || key.charAt(0).toUpperCase() + key.slice(1)
}

function renderCustomLabel({ name, value, percent }: any) {
  if (percent < 0.05) return null
  return `${(percent * 100).toFixed(0)}%`
}

interface MetricCardProps {
  title: string
  value: number
  icon: React.ComponentType<{ className?: string }>
  color: "green" | "yellow" | "red" | "blue"
  trend?: string
}

function MetricCard({ title, value, icon: Icon, color, trend }: MetricCardProps) {
  const colorClasses = {
    green: "bg-green-50 border-green-200 text-green-900",
    yellow: "bg-yellow-50 border-yellow-200 text-yellow-900",
    red: "bg-red-50 border-red-200 text-red-900",
    blue: "bg-blue-50 border-blue-200 text-blue-900",
  }

  const iconColorClasses = {
    green: "text-green-600",
    yellow: "text-yellow-600",
    red: "text-red-600",
    blue: "text-blue-600",
  }

  return (
    <div className={`rounded-lg border p-6 ${colorClasses[color]}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium">{title}</p>
          <p className="text-3xl font-bold mt-2">{value}</p>
          {trend && <p className="text-xs mt-2 opacity-75">{trend} this month</p>}
        </div>
        <Icon className={`w-8 h-8 ${iconColorClasses[color]} opacity-50`} />
      </div>
    </div>
  )
}
