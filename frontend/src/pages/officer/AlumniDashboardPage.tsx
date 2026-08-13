import React, { useEffect, useState } from "react"
import { useAuthStore } from "@/store/authStore"
import axios from "axios"
import { Button } from "@/components/ui/Button"
import { Card } from "@/components/ui/Card"

interface AlumniMember {
  member_id: string
  name: string
  graduation_year: number
  employment_status: string
}

interface EventInfo {
  event_id: string
  event_name: string
  event_date: string
  attendance: number
}

interface JobPosting {
  posting_id: string
  job_title: string
  company: string
  posted_date: string
}

interface AlumniDashboardData {
  total_alumni: number
  active_members: number
  upcoming_events: number
  job_postings: number
  alumni_members: AlumniMember[]
  events: EventInfo[]
  job_postings_list: JobPosting[]
}

export default function AlumniDashboardPage() {
  const { user } = useAuthStore()
  const [data, setData] = useState<AlumniDashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedTab, setSelectedTab] = useState<"overview" | "members" | "events" | "jobs">("overview")

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const token = localStorage.getItem("access_token")
        if (!token) return

        const response = await axios.get(`/api/v1/officer/dashboard/alumni`, {
          headers: { Authorization: `Bearer ${token}` },
        })

        setData(response.data)
      } catch (error) {
        console.error("Failed to load Alumni dashboard:", error)
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
          <h1 className="text-3xl font-bold text-gray-900">Alumni Association Dashboard</h1>
          <p className="text-gray-600 mt-2">Welcome, {user?.first_name || "Alumni Officer"}</p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Total Alumni</div>
            <div className="mt-2 text-3xl font-bold text-blue-600">{data.total_alumni}</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Active Members</div>
            <div className="mt-2 text-3xl font-bold text-green-600">{data.active_members}</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Upcoming Events</div>
            <div className="mt-2 text-3xl font-bold text-purple-600">{data.upcoming_events}</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Job Postings</div>
            <div className="mt-2 text-3xl font-bold text-orange-600">{data.job_postings}</div>
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
              onClick={() => setSelectedTab("members")}
              className={`px-6 py-4 font-medium ${
                selectedTab === "members"
                  ? "border-b-2 border-blue-600 text-blue-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Members
            </button>
            <button
              onClick={() => setSelectedTab("events")}
              className={`px-6 py-4 font-medium ${
                selectedTab === "events"
                  ? "border-b-2 border-blue-600 text-blue-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Events
            </button>
            <button
              onClick={() => setSelectedTab("jobs")}
              className={`px-6 py-4 font-medium ${
                selectedTab === "jobs"
                  ? "border-b-2 border-blue-600 text-blue-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Job Board
            </button>
          </div>

          <div className="p-6">
            {/* Overview Tab */}
            {selectedTab === "overview" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Alumni Community Overview</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-lg">
                      <div className="text-sm text-gray-600">Total Alumni</div>
                      <div className="text-3xl font-bold text-blue-600 mt-2">{data.total_alumni}</div>
                      <p className="text-sm text-gray-600 mt-2">All graduated members</p>
                    </div>

                    <div className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-lg">
                      <div className="text-sm text-gray-600">Active Members</div>
                      <div className="text-3xl font-bold text-green-600 mt-2">{data.active_members}</div>
                      <p className="text-sm text-gray-600 mt-2">
                        {((data.active_members / data.total_alumni) * 100).toFixed(1)}% engagement
                      </p>
                    </div>

                    <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-lg">
                      <div className="text-sm text-gray-600">Community Pulse</div>
                      <div className="text-3xl font-bold text-purple-600 mt-2">{data.upcoming_events}</div>
                      <p className="text-sm text-gray-600 mt-2">Events this month</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Members Tab */}
            {selectedTab === "members" && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Alumni Members</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Name</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Graduation Year</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Employment Status</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.alumni_members.map((member) => (
                        <tr key={member.member_id} className="border-b hover:bg-gray-50">
                          <td className="py-3 px-4 text-gray-900 font-medium">{member.name}</td>
                          <td className="py-3 px-4 text-gray-700">{member.graduation_year}</td>
                          <td className="py-3 px-4">
                            <span
                              className={`px-3 py-1 rounded-full text-sm font-medium ${
                                member.employment_status === "employed"
                                  ? "bg-green-100 text-green-800"
                                  : "bg-yellow-100 text-yellow-800"
                              }`}
                            >
                              {member.employment_status.charAt(0).toUpperCase() +
                                member.employment_status.slice(1)}
                            </span>
                          </td>
                          <td className="py-3 px-4">
                            <Button className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 text-sm">
                              Profile
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Events Tab */}
            {selectedTab === "events" && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Upcoming Events ({data.upcoming_events})</h3>
                <div className="space-y-4">
                  {data.events.map((event) => (
                    <div key={event.event_id} className="p-4 border rounded-lg hover:shadow-md transition">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="font-semibold text-gray-900">{event.event_name}</div>
                          <div className="text-sm text-gray-600">Date: {event.event_date}</div>
                          <div className="text-sm text-gray-600">Attendees: {event.attendance}</div>
                        </div>
                        <Button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 text-sm">
                          View Event
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Jobs Tab */}
            {selectedTab === "jobs" && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Job Postings ({data.job_postings})</h3>
                <div className="space-y-3">
                  {data.job_postings_list.map((job) => (
                    <div key={job.posting_id} className="p-4 border rounded-lg hover:shadow-md transition">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="font-semibold text-gray-900">{job.job_title}</div>
                          <div className="text-sm text-gray-600">Company: {job.company}</div>
                          <div className="text-sm text-gray-600">Posted: {job.posted_date}</div>
                        </div>
                        <Button className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 text-sm">
                          Apply
                        </Button>
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
