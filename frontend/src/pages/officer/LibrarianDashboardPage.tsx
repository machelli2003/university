import React, { useEffect, useState } from "react"
import { useAuthStore } from "@/store/authStore"
import axios from "axios"
import { Button } from "@/components/ui/Button"
import { Card } from "@/components/ui/Card"

interface BookInfo {
  book_id: string
  title: string
  isbn: string
  total_copies: number
  available_copies: number
}

interface CheckoutRecord {
  checkout_id: string
  member_name: string
  book_title: string
  checkout_date: string
  due_date: string
  status: "active" | "overdue"
}

interface LibrarianDashboardData {
  total_books: number
  available_books: number
  checked_out_books: number
  overdue_books: number
  total_members: number
  recent_checkouts: CheckoutRecord[]
  top_books: BookInfo[]
}

export default function LibrarianDashboardPage() {
  const { user } = useAuthStore()
  const [data, setData] = useState<LibrarianDashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedTab, setSelectedTab] = useState<"overview" | "inventory" | "checkouts" | "members">("overview")

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const token = localStorage.getItem("access_token")
        if (!token) return

        const response = await axios.get(`/api/v1/officer/dashboard/librarian`, {
          headers: { Authorization: `Bearer ${token}` },
        })

        setData(response.data)
      } catch (error) {
        console.error("Failed to load Librarian dashboard:", error)
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
          <h1 className="text-3xl font-bold text-gray-900">Library Dashboard</h1>
          <p className="text-gray-600 mt-2">Welcome, {user?.first_name || "Librarian"}</p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Total Books</div>
            <div className="mt-2 text-3xl font-bold text-blue-600">{data.total_books}</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Available</div>
            <div className="mt-2 text-3xl font-bold text-green-600">{data.available_books}</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Checked Out</div>
            <div className="mt-2 text-3xl font-bold text-purple-600">{data.checked_out_books}</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Overdue</div>
            <div className="mt-2 text-3xl font-bold text-red-600">{data.overdue_books}</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Members</div>
            <div className="mt-2 text-3xl font-bold text-orange-600">{data.total_members}</div>
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
              onClick={() => setSelectedTab("inventory")}
              className={`px-6 py-4 font-medium ${
                selectedTab === "inventory"
                  ? "border-b-2 border-blue-600 text-blue-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Inventory
            </button>
            <button
              onClick={() => setSelectedTab("checkouts")}
              className={`px-6 py-4 font-medium ${
                selectedTab === "checkouts"
                  ? "border-b-2 border-blue-600 text-blue-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Checkouts
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
          </div>

          <div className="p-6">
            {/* Overview Tab */}
            {selectedTab === "overview" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Library Summary</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-lg">
                      <div className="text-sm text-gray-600">Collection Status</div>
                      <div className="mt-4">
                        <div className="flex justify-between text-sm mb-2">
                          <span>Available</span>
                          <span className="font-semibold">{data.available_books}</span>
                        </div>
                        <div className="w-full bg-blue-200 rounded-full h-2">
                          <div
                            className="bg-green-500 h-2 rounded-full"
                            style={{
                              width: `${(data.available_books / data.total_books) * 100}%`,
                            }}
                          ></div>
                        </div>
                        <div className="text-sm text-gray-600 mt-2">Out of {data.total_books} total</div>
                      </div>
                    </div>

                    <div className="bg-gradient-to-br from-red-50 to-red-100 p-6 rounded-lg">
                      <div className="text-sm text-gray-600">Overdue Items</div>
                      <div className="mt-4">
                        <div className="text-3xl font-bold text-red-600">{data.overdue_books}</div>
                        <p className="text-sm text-gray-600 mt-2">Requiring immediate action</p>
                        <Button className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 text-sm mt-3">
                          View Overdue
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Inventory Tab */}
            {selectedTab === "inventory" && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Books in Collection</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {data.top_books.map((book) => (
                    <div key={book.book_id} className="p-4 border rounded-lg hover:shadow-md transition">
                      <div className="font-semibold text-gray-900">{book.title}</div>
                      <div className="text-sm text-gray-600 mt-1">ISBN: {book.isbn}</div>
                      <div className="text-sm text-gray-600">Available: {book.available_copies}/{book.total_copies}</div>
                      <div className="w-full bg-gray-300 rounded-full h-2 mt-2">
                        <div
                          className="bg-blue-500 h-2 rounded-full"
                          style={{
                            width: `${(book.available_copies / book.total_copies) * 100}%`,
                          }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Checkouts Tab */}
            {selectedTab === "checkouts" && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Checkouts</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Member</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Book</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Due Date</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Status</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.recent_checkouts.map((record) => (
                        <tr key={record.checkout_id} className="border-b hover:bg-gray-50">
                          <td className="py-3 px-4 text-gray-900">{record.member_name}</td>
                          <td className="py-3 px-4 text-gray-700">{record.book_title}</td>
                          <td className="py-3 px-4 text-gray-700">{record.due_date}</td>
                          <td className="py-3 px-4">
                            <span
                              className={`px-3 py-1 rounded-full text-sm font-medium ${
                                record.status === "active"
                                  ? "bg-green-100 text-green-800"
                                  : "bg-red-100 text-red-800"
                              }`}
                            >
                              {record.status.charAt(0).toUpperCase() + record.status.slice(1)}
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

            {/* Members Tab */}
            {selectedTab === "members" && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Library Members</h3>
                <div className="bg-blue-50 p-6 rounded-lg">
                  <div className="text-sm text-gray-600">Total Active Members</div>
                  <div className="text-4xl font-bold text-blue-600 mt-2">{data.total_members}</div>
                  <p className="text-sm text-gray-600 mt-2">All active library cardholders</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
