import { useState } from "react"
import { AppShell } from "@/components/layout/AppShell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Select } from "@/components/ui/Select"
import { ErrorAlert, SuccessAlert, Spinner } from "@/components/ui/Feedback"
import { usePayments, useConfirmPayment, useRejectPayment, useRefundPayment, useFeeStructures, useScholarships } from "@/hooks/useFinance"
import { formatCurrency } from "@/lib/utils"
import type { ScholarshipResponse, FeeStructureResponse } from "@/types/finance"
import { FinancePaymentsTable } from "@/components/finance/FinancePaymentsTable"

const FEE_TYPES = ["tuition", "hostel", "library", "registration", "exam", "other"]

export default function FinanceOfficerPage() {
  const [paymentFilters, setPaymentFilters] = useState({ student_id: "", status: "", fee_type: "" })
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const paymentsQuery = usePayments(paymentFilters)
  const confirmMutation = useConfirmPayment()
  const rejectMutation = useRejectPayment()
  const refundMutation = useRefundPayment()
  const feeQuery = useFeeStructures()
  const scholarshipQuery = useScholarships()

  const handleConfirm = async (id: string) => {
    setErrorMessage(null)
    setSuccessMessage(null)
    try {
      await confirmMutation.mutateAsync(id)
      setSuccessMessage("Payment confirmed successfully.")
      paymentsQuery.refetch()
    } catch (error) {
      setErrorMessage("Unable to confirm payment.")
    }
  }

  const handleReject = async (id: string) => {
    setErrorMessage(null)
    setSuccessMessage(null)
    try {
      await rejectMutation.mutateAsync({ paymentId: id })
      setSuccessMessage("Payment rejected successfully.")
      paymentsQuery.refetch()
    } catch (error) {
      setErrorMessage("Unable to reject payment.")
    }
  }

  const handleRefund = async (id: string) => {
    setErrorMessage(null)
    setSuccessMessage(null)
    try {
      await refundMutation.mutateAsync(id)
      setSuccessMessage("Payment refunded successfully.")
      paymentsQuery.refetch()
    } catch (error) {
      setErrorMessage("Unable to refund payment.")
    }
  }

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink mb-1">Finance Officer Dashboard</h1>
          <p className="text-cocoa-400 mb-6">Manage fee collection, payment reconciliation, scholarships, and student balances.</p>
        </div>

        {successMessage && <SuccessAlert message={successMessage} />}
        {errorMessage && <ErrorAlert message={errorMessage} />}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardHeader><CardTitle>Fee Structures</CardTitle></CardHeader>
            <CardContent>
              <p className="text-sm text-cocoa-500">Configure tuition, hostel, and academic fees by programme and year.</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Scholarships</CardTitle></CardHeader>
            <CardContent>
              <p className="text-sm text-cocoa-500">Award and review financial aid and fee waivers.</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Reconciliation</CardTitle></CardHeader>
            <CardContent>
              <p className="text-sm text-cocoa-500">Confirm, reject, or refund manual payments.</p>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader><CardTitle>Payment Reconciliation</CardTitle></CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-3 mb-4">
              <Input
                label="Student ID"
                value={paymentFilters.student_id}
                onChange={(event) => setPaymentFilters((prev) => ({ ...prev, student_id: event.target.value }))}
              />
              <Select
                label="Status"
                value={paymentFilters.status}
                onChange={(event) => setPaymentFilters((prev) => ({ ...prev, status: event.target.value }))}
              >
                <option value="">All</option>
                <option value="pending">Pending</option>
                <option value="success">Success</option>
                <option value="failed">Failed</option>
              </Select>
              <Select
                label="Fee Type"
                value={paymentFilters.fee_type}
                onChange={(event) => setPaymentFilters((prev) => ({ ...prev, fee_type: event.target.value }))}
              >
                <option value="">All</option>
                {FEE_TYPES.map((type) => (
                  <option key={type} value={type} className="capitalize">{type}</option>
                ))}
              </Select>
              <Button onClick={() => paymentsQuery.refetch()} variant="secondary" className="self-end">
                Refresh
              </Button>
            </div>

            {paymentsQuery.isLoading && <Spinner />}
            {paymentsQuery.isError && <p className="text-sm text-red-600">Unable to load payments.</p>}
            {paymentsQuery.data && paymentsQuery.data.length === 0 && <p className="text-sm text-cocoa-400">No payment records found.</p>}
            {paymentsQuery.data && paymentsQuery.data.length > 0 && (
              <FinancePaymentsTable
                payments={paymentsQuery.data}
                onConfirm={handleConfirm}
                onReject={handleReject}
                onRefund={handleRefund}
              />
            )}
          </CardContent>
        </Card>

        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader><CardTitle>Fee Structures</CardTitle></CardHeader>
            <CardContent>
              {feeQuery.isLoading && <Spinner />}
              {feeQuery.isError && <p className="text-sm text-red-600">Unable to load fee structures.</p>}
              {feeQuery.data && feeQuery.data.length === 0 && <p className="text-sm text-cocoa-400">No fee structures available.</p>}
              {feeQuery.data && feeQuery.data.length > 0 && (
                <div className="space-y-3">
                  {feeQuery.data.map((structure: FeeStructureResponse) => (
                    <div key={structure.id} className="rounded-lg border border-cocoa-100 p-4">
                      <p className="font-semibold text-ink">{structure.academic_year}</p>
                      <p className="text-sm text-cocoa-500">Programme: {structure.programme_id || "Default"}</p>
                      <p className="text-sm text-cocoa-500">Level: {structure.level || "All"}</p>
                      <div className="mt-2 text-sm text-cocoa-700 space-y-1">
                        {Object.entries(structure.fees).map(([key, value]) => (
                          <p key={key}>{key}: {formatCurrency(value)}</p>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Scholarship Awards</CardTitle></CardHeader>
            <CardContent>
              {scholarshipQuery.isLoading && <Spinner />}
              {scholarshipQuery.isError && <p className="text-sm text-red-600">Unable to load scholarships.</p>}
              {scholarshipQuery.data && scholarshipQuery.data.length === 0 && <p className="text-sm text-cocoa-400">No scholarships available.</p>}
              {scholarshipQuery.data && scholarshipQuery.data.length > 0 && (
                <div className="space-y-3">
                  {scholarshipQuery.data.map((scholarship: ScholarshipResponse) => (
                    <div key={scholarship.id} className="rounded-lg border border-cocoa-100 p-4">
                      <p className="font-semibold text-ink">{scholarship.name}</p>
                      <p className="text-sm text-cocoa-500">Student: {scholarship.student_id}</p>
                      <p className="text-sm text-cocoa-500">Type: {scholarship.scholarship_type}</p>
                      <p className="text-sm text-cocoa-500">Amount: {formatCurrency(scholarship.amount)}</p>
                      {scholarship.percentage && <p className="text-sm text-cocoa-500">Percent: {scholarship.percentage}%</p>}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </AppShell>
  )
}
