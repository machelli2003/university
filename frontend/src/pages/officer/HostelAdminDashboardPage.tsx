import React, { useEffect, useState } from "react"
import { AppShell } from "@/components/layout/AppShell"
import { useAuthStore } from "@/store/authStore"
import { apiClient, getErrorMessage } from "@/services/api/client"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Select } from "@/components/ui/Select"
import { Badge } from "@/components/ui/Badge"
import { Spinner, ErrorAlert, SuccessAlert } from "@/components/ui/Feedback"
import {
  Building2,
  Bed,
  Wrench,
  UserCheck,
  PlusCircle,
  BarChart3,
  RefreshCw,
  Home,
  CheckCircle2,
  AlertTriangle,
} from "lucide-react"

interface HostelInfo {
  hostel_id: string
  hostel_name: string
  total_beds: number
  occupied_beds: number
}

interface MaintenanceRequest {
  request_id: string
  hostel_name: string
  issue: string
  status: "pending" | "in-progress" | "completed"
  submitted_date: string
}

interface BedRequest {
  request_id: string
  student_name: string
  hostel_preference: string
  status: "approved" | "pending" | "rejected"
}

interface HostelDashboardData {
  total_hostels: number
  total_beds: number
  occupied_beds: number
  occupancy_rate: number
  pending_requests: number
  pending_maintenance: number
  hostels: HostelInfo[]
  maintenance_requests: MaintenanceRequest[]
  bed_requests: BedRequest[]
}

interface HallItem {
  id: string
  name: string
  capacity: number
  gender?: string
  is_active?: boolean
}

export default function HostelAdminDashboardPage() {
  const { user } = useAuthStore()
  const [data, setData] = useState<HostelDashboardData | null>(null)
  const [halls, setHalls] = useState<HallItem[]>([])
  const [loading, setLoading] = useState(true)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)
  const [isForbidden, setIsForbidden] = useState(false)
  const [selectedTab, setSelectedTab] = useState<"overview" | "occupancy" | "maintenance" | "requests" | "manage">("overview")

  // Create Hall Form State
  const [newHallName, setNewHallName] = useState("")
  const [newHallCapacity, setNewHallCapacity] = useState("100")
  const [newHallGender, setNewHallGender] = useState("mixed")
  const [isCreatingHall, setIsCreatingHall] = useState(false)

  // Create Room Form State
  const [selectedHallForRoom, setSelectedHallForRoom] = useState("")
  const [newRoomNumber, setNewRoomNumber] = useState("")
  const [newRoomCapacity, setNewRoomCapacity] = useState("4")
  const [newRoomType, setNewRoomType] = useState("quad")
  const [isCreatingRoom, setIsCreatingRoom] = useState(false)

  const [actionSuccessMsg, setActionSuccessMsg] = useState<string | null>(null)
  const [actionErrorMsg, setActionErrorMsg] = useState<string | null>(null)

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      setErrorMsg(null)
      setIsForbidden(false)

      const [dashRes, hallsRes] = await Promise.allSettled([
        apiClient.get(`/officer/dashboard/hostel`),
        apiClient.get(`/accommodation/halls`),
      ])

      if (dashRes.status === "fulfilled") {
        setData(dashRes.value.data)
      } else {
        const err = dashRes.reason
        if (err?.response?.status === 403) {
          setIsForbidden(true)
        } else {
          setErrorMsg(getErrorMessage(err))
        }
      }

      if (hallsRes.status === "fulfilled") {
        setHalls(hallsRes.value.data)
      }
    } catch (error: any) {
      console.error("Failed to load Hostel dashboard:", error)
      setErrorMsg(getErrorMessage(error))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const handleCreateHall = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newHallName) return
    setIsCreatingHall(true)
    setActionSuccessMsg(null)
    setActionErrorMsg(null)

    try {
      await apiClient.post("/accommodation/halls", {
        name: newHallName,
        capacity: parseInt(newHallCapacity, 10) || 100,
        gender: newHallGender,
        is_active: true,
      })
      setActionSuccessMsg(`Hall "${newHallName}" created successfully!`)
      setNewHallName("")
      setNewHallCapacity("100")
      fetchDashboardData()
    } catch (err: any) {
      setActionErrorMsg(getErrorMessage(err))
    } finally {
      setIsCreatingHall(false)
    }
  }

  const handleCreateRoom = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedHallForRoom || !newRoomNumber) return
    setIsCreatingRoom(true)
    setActionSuccessMsg(null)
    setActionErrorMsg(null)

    try {
      await apiClient.post("/accommodation/rooms", {
        hall_id: selectedHallForRoom,
        room_number: newRoomNumber,
        capacity: parseInt(newRoomCapacity, 10) || 4,
        room_type: newRoomType,
      })
      setActionSuccessMsg(`Room "${newRoomNumber}" added successfully!`)
      setNewRoomNumber("")
      fetchDashboardData()
    } catch (err: any) {
      setActionErrorMsg(getErrorMessage(err))
    } finally {
      setIsCreatingRoom(false)
    }
  }

  return (
    <AppShell>
      <div className="space-y-6">
        {/* Header Title */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="font-display text-2xl font-semibold text-ink mb-1">Hostel Management Workspace</h1>
            <p className="text-cocoa-400">
              Welcome, {user?.first_name || "Hostel Administrator"}. Oversee hall allocations, room inventory, and maintenance.
            </p>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={fetchDashboardData}
            isLoading={loading}
            className="self-start md:self-auto border-cocoa-200 text-cocoa-700 hover:bg-cocoa-50"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh Data
          </Button>
        </div>

        {/* Global Notifications */}
        {actionSuccessMsg && <SuccessAlert message={actionSuccessMsg} />}
        {actionErrorMsg && <ErrorAlert message={actionErrorMsg} />}

        {loading ? (
          <div className="flex items-center justify-center p-12">
            <Spinner />
          </div>
        ) : isForbidden ? (
          <Card className="max-w-md mx-auto p-6 text-center shadow-md">
            <div className="w-12 h-12 rounded-full bg-amber-50 border border-amber-200 text-amber-600 flex items-center justify-center mx-auto mb-4">
              <AlertTriangle className="w-6 h-6" />
            </div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Access Restricted</h2>
            <p className="text-sm text-cocoa-500 mb-4">
              The Hostel Management Workspace is reserved for Hostel Managers, Accommodation Officers, and University Management.
            </p>
            <p className="text-xs text-cocoa-400 mb-6">
              If you are a student looking for room booking or fee clearance, please visit the Student Accommodation Portal.
            </p>
            <a
              href="/accommodation"
              className="inline-block bg-cocoa-900 text-white text-sm font-medium px-5 py-2.5 rounded-lg hover:bg-cocoa-800 transition-colors"
            >
              Go to Student Accommodation Portal
            </a>
          </Card>
        ) : !data ? (
          <Card className="max-w-md mx-auto p-6 text-center">
            <h2 className="text-lg font-semibold text-red-600 mb-2">Failed to Load Dashboard Data</h2>
            <p className="text-sm text-cocoa-500 mb-4">{errorMsg || "Unable to retrieve hostel metrics."}</p>
            <Button onClick={fetchDashboardData}>Retry Loading</Button>
          </Card>
        ) : (
          <>
            {/* Quick Stats Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
              <Card className="p-5 border-l-4 border-l-cocoa-600">
                <div className="flex items-center justify-between">
                  <p className="text-xs font-semibold text-cocoa-400 uppercase tracking-wider">Total Halls</p>
                  <Building2 className="h-5 w-5 text-cocoa-600" />
                </div>
                <p className="text-2xl font-bold text-ink mt-2">{data.total_hostels}</p>
              </Card>

              <Card className="p-5 border-l-4 border-l-green-600">
                <div className="flex items-center justify-between">
                  <p className="text-xs font-semibold text-cocoa-400 uppercase tracking-wider">Total Beds</p>
                  <Bed className="h-5 w-5 text-green-600" />
                </div>
                <p className="text-2xl font-bold text-green-700 mt-2">{data.total_beds}</p>
              </Card>

              <Card className="p-5 border-l-4 border-l-purple-600">
                <div className="flex items-center justify-between">
                  <p className="text-xs font-semibold text-cocoa-400 uppercase tracking-wider">Occupied Beds</p>
                  <UserCheck className="h-5 w-5 text-purple-600" />
                </div>
                <p className="text-2xl font-bold text-purple-700 mt-2">{data.occupied_beds}</p>
              </Card>

              <Card className="p-5 border-l-4 border-l-amber-500">
                <div className="flex items-center justify-between">
                  <p className="text-xs font-semibold text-cocoa-400 uppercase tracking-wider">Occupancy Rate</p>
                  <BarChart3 className="h-5 w-5 text-amber-500" />
                </div>
                <p className="text-2xl font-bold text-amber-700 mt-2">{data.occupancy_rate.toFixed(1)}%</p>
              </Card>

              <Card className="p-5 border-l-4 border-l-red-500">
                <div className="flex items-center justify-between">
                  <p className="text-xs font-semibold text-cocoa-400 uppercase tracking-wider">Pending Maintenance</p>
                  <Wrench className="h-5 w-5 text-red-500" />
                </div>
                <p className="text-2xl font-bold text-red-700 mt-2">{data.pending_maintenance}</p>
              </Card>
            </div>

            {/* Main Tabs Navigation */}
            <Card>
              <CardHeader className="border-b border-cocoa-100 pb-0">
                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => setSelectedTab("overview")}
                    className={`flex items-center gap-2 pb-3 px-4 text-sm font-medium border-b-2 transition-colors ${
                      selectedTab === "overview"
                        ? "border-cocoa-900 text-cocoa-900 font-semibold"
                        : "border-transparent text-cocoa-500 hover:text-cocoa-700"
                    }`}
                  >
                    <BarChart3 className="h-4 w-4" />
                    Overview
                  </button>

                  <button
                    onClick={() => setSelectedTab("occupancy")}
                    className={`flex items-center gap-2 pb-3 px-4 text-sm font-medium border-b-2 transition-colors ${
                      selectedTab === "occupancy"
                        ? "border-cocoa-900 text-cocoa-900 font-semibold"
                        : "border-transparent text-cocoa-500 hover:text-cocoa-700"
                    }`}
                  >
                    <Building2 className="h-4 w-4" />
                    Halls &amp; Occupancy
                  </button>

                  <button
                    onClick={() => setSelectedTab("maintenance")}
                    className={`flex items-center gap-2 pb-3 px-4 text-sm font-medium border-b-2 transition-colors ${
                      selectedTab === "maintenance"
                        ? "border-cocoa-900 text-cocoa-900 font-semibold"
                        : "border-transparent text-cocoa-500 hover:text-cocoa-700"
                    }`}
                  >
                    <Wrench className="h-4 w-4" />
                    Maintenance ({data.pending_maintenance})
                  </button>

                  <button
                    onClick={() => setSelectedTab("requests")}
                    className={`flex items-center gap-2 pb-3 px-4 text-sm font-medium border-b-2 transition-colors ${
                      selectedTab === "requests"
                        ? "border-cocoa-900 text-cocoa-900 font-semibold"
                        : "border-transparent text-cocoa-500 hover:text-cocoa-700"
                    }`}
                  >
                    <UserCheck className="h-4 w-4" />
                    Bed Allocations
                  </button>

                  <button
                    onClick={() => setSelectedTab("manage")}
                    className={`flex items-center gap-2 pb-3 px-4 text-sm font-medium border-b-2 transition-colors ${
                      selectedTab === "manage"
                        ? "border-cocoa-900 text-cocoa-900 font-semibold"
                        : "border-transparent text-cocoa-500 hover:text-cocoa-700"
                    }`}
                  >
                    <PlusCircle className="h-4 w-4" />
                    Create Hall / Room
                  </button>
                </div>
              </CardHeader>

              <CardContent className="pt-6">
                {/* TAB 1: OVERVIEW */}
                {selectedTab === "overview" && (
                  <div className="space-y-6">
                    <div>
                      <h3 className="text-base font-semibold text-ink mb-3">Hostel System Summary</h3>
                      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <div className="bg-cocoa-50 border border-cocoa-100 p-4 rounded-lg">
                          <p className="text-xs text-cocoa-500 font-medium">Active Hostels</p>
                          <p className="text-xl font-bold text-cocoa-900 mt-1">{data.total_hostels}</p>
                        </div>
                        <div className="bg-green-50 border border-green-100 p-4 rounded-lg">
                          <p className="text-xs text-green-700 font-medium">Total Bed Capacity</p>
                          <p className="text-xl font-bold text-green-900 mt-1">{data.total_beds}</p>
                        </div>
                        <div className="bg-purple-50 border border-purple-100 p-4 rounded-lg">
                          <p className="text-xs text-purple-700 font-medium">Current Occupants</p>
                          <p className="text-xl font-bold text-purple-900 mt-1">{data.occupied_beds}</p>
                        </div>
                        <div className="bg-amber-50 border border-amber-100 p-4 rounded-lg">
                          <p className="text-xs text-amber-700 font-medium">Available Vacancies</p>
                          <p className="text-xl font-bold text-amber-900 mt-1">{Math.max(0, data.total_beds - data.occupied_beds)}</p>
                        </div>
                      </div>
                    </div>

                    <div className="rounded-xl bg-cocoa-50/70 border border-cocoa-100 p-6">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
                        <div>
                          <h4 className="font-semibold text-ink">University Occupancy Progress</h4>
                          <p className="text-xs text-cocoa-400">
                            {data.occupied_beds} of {data.total_beds} beds filled institutional-wide
                          </p>
                        </div>
                        <span className="text-2xl font-bold text-cocoa-800">{data.occupancy_rate.toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-cocoa-200 rounded-full h-3">
                        <div
                          className="bg-cocoa-800 h-3 rounded-full transition-all duration-500"
                          style={{ width: `${Math.min(data.occupancy_rate, 100)}%` }}
                        />
                      </div>
                    </div>
                  </div>
                )}

                {/* TAB 2: OCCUPANCY BREAKDOWN */}
                {selectedTab === "occupancy" && (
                  <div className="space-y-4">
                    <h3 className="text-base font-semibold text-ink">Halls of Residence Occupancy</h3>
                    {data.hostels.length === 0 ? (
                      <div className="p-8 text-center border border-dashed border-cocoa-200 rounded-xl bg-cocoa-50/40">
                        <Building2 className="h-10 w-10 text-cocoa-400 mx-auto mb-2" />
                        <p className="font-semibold text-cocoa-700">No Halls Created Yet</p>
                        <p className="text-xs text-cocoa-500 mt-1 mb-4">
                          You haven't added any halls of residence to the system.
                        </p>
                        <Button size="sm" onClick={() => setSelectedTab("manage")}>
                          <PlusCircle className="h-4 w-4 mr-2" />
                          Create Your First Hall
                        </Button>
                      </div>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {data.hostels.map((hostel) => {
                          const rate = hostel.total_beds > 0 ? (hostel.occupied_beds / hostel.total_beds) * 100 : 0
                          return (
                            <div key={hostel.hostel_id} className="p-4 rounded-lg border border-cocoa-100 bg-white hover:border-cocoa-300 transition-colors space-y-3">
                              <div className="flex items-center justify-between">
                                <span className="font-semibold text-ink text-sm flex items-center gap-2">
                                  <Home className="h-4 w-4 text-cocoa-600" />
                                  {hostel.hostel_name}
                                </span>
                                <Badge variant={rate >= 90 ? "warning" : "success"}>
                                  {rate.toFixed(0)}% Full
                                </Badge>
                              </div>
                              <div className="flex justify-between text-xs text-cocoa-500">
                                <span>Occupied: {hostel.occupied_beds} beds</span>
                                <span>Total: {hostel.total_beds} beds</span>
                              </div>
                              <div className="w-full bg-cocoa-100 rounded-full h-2">
                                <div
                                  className="bg-cocoa-700 h-2 rounded-full transition-all duration-300"
                                  style={{ width: `${Math.min(rate, 100)}%` }}
                                />
                              </div>
                            </div>
                          )
                        })}
                      </div>
                    )}
                  </div>
                )}

                {/* TAB 3: MAINTENANCE REQUESTS */}
                {selectedTab === "maintenance" && (
                  <div className="space-y-4">
                    <h3 className="text-base font-semibold text-ink">Maintenance Reports ({data.maintenance_requests.length})</h3>
                    {data.maintenance_requests.length === 0 ? (
                      <div className="p-8 text-center border border-dashed border-cocoa-200 rounded-xl bg-cocoa-50/40">
                        <Wrench className="h-10 w-10 text-cocoa-400 mx-auto mb-2" />
                        <p className="font-semibold text-cocoa-700">No Maintenance Reports</p>
                        <p className="text-xs text-cocoa-500 mt-1">There are no active or pending maintenance requests submitted.</p>
                      </div>
                    ) : (
                      <div className="overflow-x-auto border border-cocoa-100 rounded-lg">
                        <table className="w-full text-sm text-left">
                          <thead className="bg-cocoa-50 text-cocoa-700 font-semibold border-b border-cocoa-100">
                            <tr>
                              <th className="py-3 px-4">Request ID</th>
                              <th className="py-3 px-4">Hostel / Location</th>
                              <th className="py-3 px-4">Reported Issue</th>
                              <th className="py-3 px-4">Date Submitted</th>
                              <th className="py-3 px-4">Status</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-cocoa-100">
                            {data.maintenance_requests.map((m) => (
                              <tr key={m.request_id} className="hover:bg-cocoa-50/50 transition-colors">
                                <td className="py-3 px-4 font-mono text-xs text-ink">{m.request_id.substring(0, 10)}</td>
                                <td className="py-3 px-4 text-cocoa-800 font-medium">{m.hostel_name}</td>
                                <td className="py-3 px-4 text-cocoa-600">{m.issue}</td>
                                <td className="py-3 px-4 text-cocoa-400 text-xs">{m.submitted_date}</td>
                                <td className="py-3 px-4">
                                  <Badge variant={m.status === "completed" ? "success" : m.status === "in-progress" ? "info" : "warning"}>
                                    {m.status.toUpperCase()}
                                  </Badge>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                )}

                {/* TAB 4: BED REQUESTS */}
                {selectedTab === "requests" && (
                  <div className="space-y-4">
                    <h3 className="text-base font-semibold text-ink">Recent Bed Allocations</h3>
                    {data.bed_requests.length === 0 ? (
                      <div className="p-8 text-center border border-dashed border-cocoa-200 rounded-xl bg-cocoa-50/40">
                        <UserCheck className="h-10 w-10 text-cocoa-400 mx-auto mb-2" />
                        <p className="font-semibold text-cocoa-700">No Bed Allocations Yet</p>
                        <p className="text-xs text-cocoa-500 mt-1">There are currently no bed requests or student room allocations recorded.</p>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {data.bed_requests.map((r) => (
                          <div key={r.request_id} className="p-4 rounded-lg border border-cocoa-100 bg-white flex items-center justify-between">
                            <div>
                              <p className="font-medium text-sm text-ink">{r.student_name}</p>
                              <p className="text-xs text-cocoa-400">Assigned / Preferred: {r.hostel_preference}</p>
                            </div>
                            <Badge variant={r.status === "approved" ? "success" : r.status === "pending" ? "warning" : "default"}>
                              {r.status.toUpperCase()}
                            </Badge>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* TAB 5: CREATE HALL & ROOM */}
                {selectedTab === "manage" && (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Create Hall Form */}
                    <div className="border border-cocoa-100 rounded-xl p-5 bg-white space-y-4">
                      <h4 className="font-semibold text-ink text-base flex items-center gap-2">
                        <Building2 className="h-5 w-5 text-cocoa-600" />
                        Create New Hall of Residence
                      </h4>
                      <form onSubmit={handleCreateHall} className="space-y-4">
                        <Input
                          label="Hall Name"
                          placeholder="e.g. Nelson Mandela Hall"
                          value={newHallName}
                          onChange={(e) => setNewHallName(e.target.value)}
                          required
                        />

                        <Input
                          label="Total Bed Capacity"
                          type="number"
                          value={newHallCapacity}
                          onChange={(e) => setNewHallCapacity(e.target.value)}
                          required
                        />

                        <Select
                          label="Gender Restriction"
                          value={newHallGender}
                          onChange={(e) => setNewHallGender(e.target.value)}
                        >
                          <option value="mixed">Mixed (Male &amp; Female)</option>
                          <option value="male">Male Only</option>
                          <option value="female">Female Only</option>
                        </Select>

                        <Button type="submit" isLoading={isCreatingHall} className="w-full">
                          Create Hall of Residence
                        </Button>
                      </form>
                    </div>

                    {/* Add Room Form */}
                    <div className="border border-cocoa-100 rounded-xl p-5 bg-white space-y-4">
                      <h4 className="font-semibold text-ink text-base flex items-center gap-2">
                        <Bed className="h-5 w-5 text-cocoa-600" />
                        Add Room to Hall
                      </h4>
                      <form onSubmit={handleCreateRoom} className="space-y-4">
                        <Select
                          label="Select Hall"
                          value={selectedHallForRoom}
                          onChange={(e) => setSelectedHallForRoom(e.target.value)}
                          required
                        >
                          <option value="">Select a hall...</option>
                          {halls.map((h) => (
                            <option key={h.id} value={h.id}>
                              {h.name}
                            </option>
                          ))}
                        </Select>

                        <Input
                          label="Room Number"
                          placeholder="e.g. A-101"
                          value={newRoomNumber}
                          onChange={(e) => setNewRoomNumber(e.target.value)}
                          required
                        />

                        <Input
                          label="Room Capacity (Beds)"
                          type="number"
                          value={newRoomCapacity}
                          onChange={(e) => setNewRoomCapacity(e.target.value)}
                          required
                        />

                        <Select
                          label="Room Type"
                          value={newRoomType}
                          onChange={(e) => setNewRoomType(e.target.value)}
                        >
                          <option value="single">Single Bed Room</option>
                          <option value="double">Double (2 Beds)</option>
                          <option value="quad">Quad (4 Beds)</option>
                        </Select>

                        <Button type="submit" isLoading={isCreatingRoom} disabled={!selectedHallForRoom || !newRoomNumber} className="w-full">
                          Add Room to Selected Hall
                        </Button>
                      </form>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </AppShell>
  )
}
