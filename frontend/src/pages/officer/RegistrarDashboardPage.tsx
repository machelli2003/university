import { useEffect, useState } from "react"
import { AppShell } from "@/components/layout/AppShell"
import { Button } from "@/components/ui/Button"
import { apiClient, getErrorMessage } from "@/services/api/client"
import {
  PieChart,
  Pie,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts"
import { TrendingUp, Users, Award, AlertCircle, RefreshCw } from "lucide-react"

interface EnrollmentRecord {
  applicant_id: string
  student_id: string
  full_name: string
  email: string
  phone: string
  programme: string
  enrolled_date: string
  academic_standing: string
  status: string
}

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
  recent_enrollments: EnrollmentRecord[]
  pending_enrollment_verification: EnrollmentRecord[]
  students_on_probation: EnrollmentRecord[]
  graduation_eligible: EnrollmentRecord[]
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

  const fetchDashboardData = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await apiClient.get<RegistrarDashboardData>("/officer/dashboard/registrar")
      setDashboardData(response.data)
    } catch (err) {
      setError(getErrorMessage(err) || "Failed to load dashboard data")
      setDashboardData(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDashboardData()
  }, [])

  return (
    <AppShell>
      {loading && (
        <div className="flex items-center justify-center py-24">
          <div className="text-center">
            <div className="inline-block h-10 w-10 animate-spin rounded-full border-b-2 border-cocoa-700" />
            <p className="mt-4 text-cocoa-500">Loading registrar dashboard...</p>
          </div>
        </div>
      )}

      {!loading && error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4">
          <p className="text-red-700">{error}</p>
          <Button onClick={fetchDashboardData} className="mt-4">
            Retry
          </Button>
        </div>
      )}

      {!loading && !error && dashboardData && (
        <DashboardContent
          data={dashboardData}
          selectedTab={selectedTab}
          setSelectedTab={setSelectedTab}
          onRefresh={fetchDashboardData}
        />
      )}
    </AppShell>
  )
}

function DashboardContent({
  data,
  selectedTab,
  setSelectedTab,
  onRefresh,
}: {
  data: RegistrarDashboardData
  selectedTab: "overview" | "students" | "academic" | "progression"
  setSelectedTab: (tab: "overview" | "students" | "academic" | "progression") => void
  onRefresh: () => void
}) {
  const { enrollment_stats, students_by_academic_standing, students_by_level } = data
  const totalEnrolled = enrollment_stats.total_enrolled
  const standingEntries = Object.entries(students_by_academic_standing).filter(([, value]) => value > 0)
  const pieData = getPieChartData(students_by_academic_standing)
  const levels = Object.keys(students_by_level).sort()

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink">Registrar Dashboard</h1>
          <p className="mt-1 text-cocoa-400">Live enrollment, standing, and academic records</p>
        </div>
        <Button onClick={onRefresh} variant="outline" className="inline-flex items-center gap-2">
          <RefreshCw className="h-4 w-4" />
          Refresh
        </Button>
      </div>

      {totalEnrolled === 0 && (
        <div className="rounded-lg border border-cocoa-100 bg-white p-4 text-sm text-cocoa-500">
          No enrolled students yet. Counts will fill in as applicants complete enrollment.
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-5">
        <StatCard label="Total Enrolled" value={enrollment_stats.total_enrolled} hint="Students" color="text-green-600" />
        <StatCard label="Enrolled This Month" value={enrollment_stats.enrolled_this_month} hint="New students" color="text-blue-600" />
        <StatCard label="Pending Enrollment" value={enrollment_stats.pending_enrollment} hint="Verification pending" color="text-yellow-600" />
        <StatCard label="Academic Good Standing" value={students_by_academic_standing.good || 0} hint="Status: good" color="text-green-600" />
        <StatCard label="On Probation" value={students_by_academic_standing.probation || 0} hint="Academic warning" color="text-red-600" />
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div className="rounded-lg bg-white p-6 shadow-sm">
          <p className="mb-2 font-semibold text-ink">Monthly Enrollment Rate</p>
          <p className="text-4xl font-bold text-blue-600">{data.monthly_enrollment_rate.toFixed(1)}%</p>
          <p className="mt-2 text-sm text-cocoa-500">Enrolled this month vs total</p>
        </div>
        <div className="rounded-lg bg-white p-6 shadow-sm">
          <p className="mb-2 font-semibold text-ink">Verification Rate</p>
          <p className="text-4xl font-bold text-green-600">{data.verification_completion_rate.toFixed(1)}%</p>
          <p className="mt-2 text-sm text-cocoa-500">Active students vs enrolled</p>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {(["overview", "students", "academic", "progression"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setSelectedTab(tab)}
            className={`rounded-lg px-4 py-2 font-medium transition-colors ${
              selectedTab === tab
                ? "bg-cocoa-800 text-white"
                : "border border-cocoa-200 bg-white text-cocoa-700 hover:bg-cocoa-50"
            }`}
          >
            {tab === "overview" && "Overview"}
            {tab === "students" && "Students by Level"}
            {tab === "academic" && "Academic Standing"}
            {tab === "progression" && "Recent Enrollments"}
          </button>
        ))}
      </div>

      {selectedTab === "overview" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div className="rounded-lg bg-white p-6 shadow-sm">
              <h2 className="mb-4 flex items-center gap-2 text-xl font-bold text-ink">
                <Award className="h-5 w-5 text-blue-600" />
                Academic Standing Distribution
              </h2>
              {pieData.length === 0 ? (
                <p className="py-16 text-center text-cocoa-400">No standing data yet</p>
              ) : (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={renderCustomLabel}
                      outerRadius={100}
                      dataKey="value"
                    >
                      {pieData.map((entry) => (
                        <Cell key={entry.name} fill={getColorForStanding(entry.key)} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value: number) => `${value} students`} />
                  </PieChart>
                </ResponsiveContainer>
              )}
              <div className="mt-4 grid grid-cols-1 gap-2">
                {standingEntries.map(([key, value]) => (
                  <div key={key} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="h-3 w-3 rounded-full" style={{ backgroundColor: getColorForStanding(key) }} />
                      <span className="text-sm capitalize text-cocoa-700">{formatStandingLabel(key)}</span>
                    </div>
                    <span className="text-sm font-semibold text-ink">{value}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-lg bg-white p-6 shadow-sm">
              <h2 className="mb-4 flex items-center gap-2 text-xl font-bold text-ink">
                <Users className="h-5 w-5 text-green-600" />
                Students by Academic Level
              </h2>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={getBarChartData(students_by_level)} margin={{ top: 20, right: 30, left: 0, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="name" stroke="#6b7280" />
                  <YAxis allowDecimals={false} stroke="#6b7280" />
                  <Tooltip formatter={(value: number) => `${value} students`} />
                  <Bar dataKey="value" fill="#10b981" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
            <MetricCard title="Good Standing" value={students_by_academic_standing.good || 0} icon={Award} color="green" />
            <MetricCard title="On Warning" value={students_by_academic_standing.warning || 0} icon={AlertCircle} color="yellow" />
            <MetricCard title="On Probation" value={students_by_academic_standing.probation || 0} icon={TrendingUp} color="red" />
            <MetricCard title="Graduation Ready" value={data.graduation_eligible.length} icon={Award} color="blue" />
          </div>
        </div>
      )}

      {selectedTab === "students" && (
        <div className="rounded-lg bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-xl font-bold text-ink">Student Distribution by Academic Level</h2>
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
            {levels.map((level) => (
              <div key={level} className="rounded-lg border p-4 text-center">
                <p className="font-medium text-cocoa-500">Level {level}</p>
                <p className="mt-2 text-4xl font-bold text-blue-600">{students_by_level[level] || 0}</p>
                <p className="mt-2 text-sm text-cocoa-400">
                  {totalEnrolled > 0
                    ? `${(((students_by_level[level] || 0) / totalEnrolled) * 100).toFixed(1)}% of total`
                    : "0% of total"}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {selectedTab === "academic" && (
        <div className="space-y-6">
          <StandingPanel
            title={`Academic Good Standing (${students_by_academic_standing.good || 0})`}
            body="Students meeting academic requirements."
            tone="green"
          />
          <StandingPanel
            title={`Academic Warning (${students_by_academic_standing.warning || 0})`}
            body="Students with declining performance."
            tone="yellow"
          />
          <StandingPanel
            title={`On Academic Probation (${students_by_academic_standing.probation || 0})`}
            body="Students at academic risk."
            tone="red"
          />
          {data.students_on_probation.length > 0 && (
            <RecordTable title="Students currently on probation" records={data.students_on_probation} />
          )}
        </div>
      )}

      {selectedTab === "progression" && (
        <RecordTable title="Recent Student Enrollments" records={data.recent_enrollments} />
      )}
    </div>
  )
}

function StatCard({
  label,
  value,
  hint,
  color,
}: {
  label: string
  value: number
  hint: string
  color: string
}) {
  return (
    <div className="rounded-lg bg-white p-6 shadow-sm">
      <p className="text-sm font-medium text-cocoa-500">{label}</p>
      <p className={`mt-2 text-3xl font-bold ${color}`}>{value}</p>
      <p className="mt-1 text-xs text-cocoa-400">{hint}</p>
    </div>
  )
}

function StandingPanel({ title, body, tone }: { title: string; body: string; tone: "green" | "yellow" | "red" }) {
  const classes = {
    green: "border-green-200 bg-green-50 text-green-900",
    yellow: "border-yellow-200 bg-yellow-50 text-yellow-900",
    red: "border-red-200 bg-red-50 text-red-900",
  }
  return (
    <div className={`rounded-lg border p-6 ${classes[tone]}`}>
      <h3 className="mb-3 text-lg font-bold">{title}</h3>
      <p>{body}</p>
    </div>
  )
}

function RecordTable({ title, records }: { title: string; records: EnrollmentRecord[] }) {
  return (
    <div className="rounded-lg bg-white p-6 shadow-sm">
      <h2 className="mb-4 text-xl font-bold text-ink">{title}</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-cocoa-50">
            <tr>
              <th className="px-4 py-3 text-left font-medium text-ink">Student Name</th>
              <th className="px-4 py-3 text-left font-medium text-ink">Student ID</th>
              <th className="px-4 py-3 text-left font-medium text-ink">Programme</th>
              <th className="px-4 py-3 text-left font-medium text-ink">Enrolled Date</th>
              <th className="px-4 py-3 text-left font-medium text-ink">Standing</th>
            </tr>
          </thead>
          <tbody>
            {records.map((student) => (
              <tr key={`${student.student_id}-${student.applicant_id}`} className="border-t hover:bg-cocoa-50">
                <td className="px-4 py-3 font-medium text-ink">{student.full_name}</td>
                <td className="px-4 py-3 text-cocoa-600">{student.student_id}</td>
                <td className="px-4 py-3 text-cocoa-600">{student.programme}</td>
                <td className="px-4 py-3 text-cocoa-600">
                  {student.enrolled_date ? new Date(student.enrolled_date).toLocaleDateString() : "—"}
                </td>
                <td className="px-4 py-3">
                  <span className="rounded-full bg-green-100 px-2 py-1 text-xs text-green-800">
                    {formatStandingLabel(student.academic_standing)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {records.length === 0 && <div className="p-6 text-center text-cocoa-500">No records yet</div>}
      </div>
    </div>
  )
}

function getPieChartData(standingData: Record<string, number>) {
  return Object.entries(standingData)
    .filter(([, value]) => value > 0)
    .map(([key, value]) => ({
      key,
      name: formatStandingLabel(key),
      value,
    }))
}

function getBarChartData(levelData: Record<string, number>) {
  const levels = Object.keys(levelData).length ? Object.keys(levelData).sort() : ["100", "200", "300", "400"]
  return levels.map((level) => ({
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
    unassessed: "#6b7280",
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
    unassessed: "Unassessed",
  }
  return labelMap[key] || key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, " ")
}

function renderCustomLabel({ percent }: { percent?: number }) {
  if (!percent || percent < 0.05) return null
  return `${(percent * 100).toFixed(0)}%`
}

function MetricCard({
  title,
  value,
  icon: Icon,
  color,
}: {
  title: string
  value: number
  icon: typeof Award
  color: "green" | "yellow" | "red" | "blue"
}) {
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
          <p className="mt-2 text-3xl font-bold">{value}</p>
        </div>
        <Icon className={`h-8 w-8 opacity-50 ${iconColorClasses[color]}`} />
      </div>
    </div>
  )
}
