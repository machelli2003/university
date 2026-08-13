import React, { useEffect, useState } from "react"
import { useAuthStore } from "@/store/authStore"
import axios from "axios"
import { Button } from "@/components/ui/Button"
import { Card } from "@/components/ui/Card"

interface InvoiceInfo {
  invoice_id: string
  student_id: string
  amount: number
  status: "paid" | "pending" | "overdue"
  due_date: string
}

interface PaymentInfo {
  payment_id: string
  student_id: string
  amount: number
  payment_date: string
  method: string
}

interface FinanceDashboardData {
  total_invoices: number
  total_paid: number
  total_pending: number
  total_overdue: number
  total_revenue: number
  outstanding_balance: number
  payment_success_rate: number
  recent_payments: PaymentInfo[]
  pending_invoices: InvoiceInfo[]
}

export default function FinanceOfficerDashboardPage() {
  const { user } = useAuthStore()
  const [data, setData] = useState<FinanceDashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedTab, setSelectedTab] = useState<"overview" | "invoices" | "payments" | "reports">("overview")

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const token = localStorage.getItem("access_token")
        if (!token) return

        const response = await axios.get(`/api/v1/officer/dashboard/finance`, {
          headers: { Authorization: `Bearer ${token}` },
        })

        setData(response.data)
      } catch (error) {
        console.error("Failed to load Finance dashboard:", error)
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
          <h1 className="text-3xl font-bold text-gray-900">Finance Officer Dashboard</h1>
          <p className="text-gray-600 mt-2">Welcome, {user?.first_name || "Finance Officer"}</p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Total Invoices</div>
            <div className="mt-2 text-3xl font-bold text-blue-600">{data.total_invoices}</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Total Revenue</div>
            <div className="mt-2 text-3xl font-bold text-green-600">GH₵{(data.total_revenue / 1000).toFixed(1)}K</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Outstanding</div>
            <div className="mt-2 text-3xl font-bold text-orange-600">GH₵{(data.outstanding_balance / 1000).toFixed(1)}K</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Pending</div>
            <div className="mt-2 text-3xl font-bold text-yellow-600">{data.total_pending}</div>
          </Card>
          <Card className="p-6 bg-white shadow">
            <div className="text-sm font-medium text-gray-600">Success Rate</div>
            <div className="mt-2 text-3xl font-bold text-purple-600">{data.payment_success_rate.toFixed(1)}%</div>
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
              onClick={() => setSelectedTab("invoices")}
              className={`px-6 py-4 font-medium ${
                selectedTab === "invoices"
                  ? "border-b-2 border-blue-600 text-blue-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Invoices
            </button>
            <button
              onClick={() => setSelectedTab("payments")}
              className={`px-6 py-4 font-medium ${
                selectedTab === "payments"
                  ? "border-b-2 border-blue-600 text-blue-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Payments
            </button>
            <button
              onClick={() => setSelectedTab("reports")}
              className={`px-6 py-4 font-medium ${
                selectedTab === "reports"
                  ? "border-b-2 border-blue-600 text-blue-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Reports
            </button>
          </div>

          <div className="p-6">
            {/* Overview Tab */}
            {selectedTab === "overview" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Financial Overview</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-lg">
                      <div className="text-sm text-gray-600">Total Revenue</div>
                      <div className="text-3xl font-bold text-green-600 mt-2">
                        GH₵{(data.total_revenue / 1000).toFixed(1)}K
                      </div>
                      <div className="text-sm text-gray-600 mt-2">{data.total_paid} payments received</div>
                    </div>

                    <div className="bg-gradient-to-br from-orange-50 to-orange-100 p-6 rounded-lg">
                      <div className="text-sm text-gray-600">Outstanding Balance</div>
                      <div className="text-3xl font-bold text-orange-600 mt-2">
                        GH₵{(data.outstanding_balance / 1000).toFixed(1)}K
                      </div>
                      <div className="text-sm text-gray-600 mt-2">{data.total_overdue} overdue invoices</div>
                    </div>

                    <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-lg">
                      <div className="text-sm text-gray-600">Payment Success Rate</div>
                      <div className="text-3xl font-bold text-blue-600 mt-2">{data.payment_success_rate.toFixed(1)}%</div>
                      <div className="text-sm text-gray-600 mt-2">Overall collection rate</div>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Invoice Breakdown</h3>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="p-4 bg-blue-50 rounded">
                      <div className="text-sm text-gray-600">Total Invoices</div>
                      <div className="text-2xl font-bold text-blue-600 mt-1">{data.total_invoices}</div>
                    </div>
                    <div className="p-4 bg-green-50 rounded">
                      <div className="text-sm text-gray-600">Paid</div>
                      <div className="text-2xl font-bold text-green-600 mt-1">{data.total_paid}</div>
                    </div>
                    <div className="p-4 bg-yellow-50 rounded">
                      <div className="text-sm text-gray-600">Pending</div>
                      <div className="text-2xl font-bold text-yellow-600 mt-1">{data.total_pending}</div>
                    </div>
                    <div className="p-4 bg-red-50 rounded">
                      <div className="text-sm text-gray-600">Overdue</div>
                      <div className="text-2xl font-bold text-red-600 mt-1">{data.total_overdue}</div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Invoices Tab */}
            {selectedTab === "invoices" && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Pending Invoices</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Invoice ID</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Student</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Amount</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Due Date</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Status</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.pending_invoices.map((invoice) => (
                        <tr key={invoice.invoice_id} className="border-b hover:bg-gray-50">
                          <td className="py-3 px-4 text-gray-900">{invoice.invoice_id}</td>
                          <td className="py-3 px-4 text-gray-700">{invoice.student_id}</td>
                          <td className="py-3 px-4 font-medium text-gray-900">GH₵{invoice.amount}</td>
                          <td className="py-3 px-4 text-gray-700">{invoice.due_date}</td>
                          <td className="py-3 px-4">
                            <span
                              className={`px-3 py-1 rounded-full text-sm font-medium ${
                                invoice.status === "paid"
                                  ? "bg-green-100 text-green-800"
                                  : invoice.status === "pending"
                                    ? "bg-yellow-100 text-yellow-800"
                                    : "bg-red-100 text-red-800"
                              }`}
                            >
                              {invoice.status.charAt(0).toUpperCase() + invoice.status.slice(1)}
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

            {/* Payments Tab */}
            {selectedTab === "payments" && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Payments</h3>
                <div className="space-y-3">
                  {data.recent_payments.map((payment) => (
                    <div key={payment.payment_id} className="p-4 border rounded-lg hover:shadow-md transition">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="font-semibold text-gray-900">
                            Payment {payment.payment_id.substring(0, 8)}
                          </div>
                          <div className="text-sm text-gray-600">
                            Student ID: {payment.student_id} • {payment.payment_date}
                          </div>
                          <div className="text-sm text-gray-600">Method: {payment.method}</div>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-green-600">GH₵{payment.amount}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Reports Tab */}
            {selectedTab === "reports" && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Financial Reports</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="p-6 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg">
                    <div className="text-lg font-semibold text-gray-900">Collection Rate</div>
                    <div className="mt-4">
                      <div className="flex items-end justify-between">
                        <span className="text-gray-600">Collected</span>
                        <span className="text-3xl font-bold text-blue-600">
                          {data.payment_success_rate.toFixed(1)}%
                        </span>
                      </div>
                      <div className="w-full bg-blue-200 rounded-full h-2 mt-3">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{
                            width: `${data.payment_success_rate}%`,
                          }}
                        ></div>
                      </div>
                    </div>
                  </div>

                  <div className="p-6 bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg">
                    <div className="text-lg font-semibold text-gray-900">Outstanding Debt</div>
                    <div className="mt-4">
                      <div className="text-sm text-gray-600">Total Outstanding</div>
                      <div className="text-3xl font-bold text-orange-600 mt-2">
                        GH₵{(data.outstanding_balance / 1000).toFixed(1)}K
                      </div>
                      <div className="text-sm text-gray-600 mt-2">
                        From {data.total_overdue} overdue invoices
                      </div>
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
