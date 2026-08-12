import { useState } from "react"
import { useForm } from "react-hook-form"
import { AppShell } from "@/components/layout/AppShell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Select } from "@/components/ui/Select"
import { Badge, statusToVariant } from "@/components/ui/Badge"
import { ErrorAlert, SuccessAlert, Spinner } from "@/components/ui/Feedback"
import { useAuthStore } from "@/store/authStore"
import { useInitiatePayment, useVerifyPayment, usePaymentHistory } from "@/hooks/useFinance"
import { getErrorMessage } from "@/services/api/client"
import { formatCurrency, formatDate } from "@/lib/utils"
import type { InitiatePaymentRequest } from "@/types/academic"

const FEE_TYPES = ["tuition", "hostel", "library", "registration", "exam", "other"]

export default function PaymentsPage() {
  const studentId = useAuthStore((s) => s.studentId)
  const [pendingReference, setPendingReference] = useState<string | null>(null)

  const initiateMutation = useInitiatePayment()
  const verifyQuery = useVerifyPayment(pendingReference)
  const historyQuery = usePaymentHistory(studentId)

  const { register, handleSubmit, reset } = useForm<InitiatePaymentRequest>({
    defaultValues: {
      student_id: studentId ?? "",
      amount: 0,
      fee_type: "tuition",
      payment_method: "mobile_money",
    },
  })

  const onSubmit = (data: InitiatePaymentRequest) => {
    if (!studentId) return

    initiateMutation.mutate(
      { ...data, student_id: studentId, amount: Number(data.amount) },
      {
        onSuccess: (result) => {
          setPendingReference(result.payment_reference)
          window.open(result.authorization_url, "_blank")
          reset()
        },
      }
    )
  }

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-semibold text-ink mb-1">Payments</h1>
      <p className="text-cocoa-400 mb-6">Pay fees via Paystack (Mobile Money, Card, Bank Transfer).</p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader><CardTitle>Make a Payment</CardTitle></CardHeader>
          <CardContent>
            {initiateMutation.isError && <ErrorAlert message={getErrorMessage(initiateMutation.error)} />}
            {initiateMutation.isSuccess && (
              <SuccessAlert message="Redirecting to Paystack checkout in a new tab. Complete payment there, then return here." />
            )}

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <Input
                label="Amount (GHS)"
                type="number"
                step="0.01"
                min="1"
                {...register("amount", { required: true, valueAsNumber: true })}
              />

              <Select label="Fee Type" {...register("fee_type")}>
                {FEE_TYPES.map((f) => (
                  <option key={f} value={f} className="capitalize">{f}</option>
                ))}
              </Select>

              <Select label="Payment Method" {...register("payment_method")}>
                <option value="mobile_money">Mobile Money</option>
                <option value="card">Card</option>
                <option value="bank_transfer">Bank Transfer</option>
              </Select>

              <Button type="submit" isLoading={initiateMutation.isPending} className="w-full" disabled={!studentId}>
                Pay with Paystack
              </Button>
              {!studentId && (
                <p className="text-xs text-cocoa-500 mt-2">
                  Accept your offer first to create a student record before making fee payments.
                </p>
              )}
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Verify Recent Payment</CardTitle></CardHeader>
          <CardContent>
            {!pendingReference && (
              <p className="text-sm text-cocoa-400">
                After completing checkout on Paystack, come back here — verification runs automatically.
              </p>
            )}
            {pendingReference && verifyQuery.isLoading && (
              <div className="flex items-center gap-2 text-sm text-cocoa-500">
                <Spinner /> Verifying payment reference {pendingReference}...
              </div>
            )}
            {verifyQuery.data?.verified && (
              <SuccessAlert message={`Payment confirmed. Receipt: ${verifyQuery.data.receipt_number}`} />
            )}
            {verifyQuery.data && !verifyQuery.data.verified && (
              <ErrorAlert message={verifyQuery.data.message || "Payment not yet confirmed."} />
            )}
          </CardContent>
        </Card>
      </div>

      <Card className="mt-6">
        <CardHeader><CardTitle>Payment History</CardTitle></CardHeader>
        <CardContent>
          {historyQuery.isLoading && <Spinner />}
          {historyQuery.data && historyQuery.data.length === 0 && (
            <p className="text-sm text-cocoa-400">No payments yet.</p>
          )}
          {historyQuery.data && historyQuery.data.length > 0 && (
            <table className="w-full text-sm">
              <thead className="bg-cocoa-50 text-cocoa-500 text-left">
                <tr>
                  <th className="px-3 py-2 font-medium">Fee Type</th>
                  <th className="px-3 py-2 font-medium">Amount</th>
                  <th className="px-3 py-2 font-medium">Status</th>
                  <th className="px-3 py-2 font-medium">Date</th>
                  <th className="px-3 py-2 font-medium">Receipt</th>
                </tr>
              </thead>
              <tbody>
                {historyQuery.data.map((p) => (
                  <tr key={p.id} className="border-t border-cocoa-50">
                    <td className="px-3 py-2 capitalize">{p.fee_type}</td>
                    <td className="px-3 py-2 font-mono">{formatCurrency(p.amount)}</td>
                    <td className="px-3 py-2"><Badge variant={statusToVariant(p.status)}>{p.status}</Badge></td>
                    <td className="px-3 py-2 text-cocoa-400">{formatDate(p.payment_date)}</td>
                    <td className="px-3 py-2 font-mono text-cocoa-400">{p.receipt_number || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </CardContent>
      </Card>
    </AppShell>
  )
}
