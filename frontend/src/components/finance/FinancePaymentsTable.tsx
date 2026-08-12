import { Button } from "@/components/ui/Button"
import { Badge, statusToVariant } from "@/components/ui/Badge"
import type { PaymentListItem } from "@/types/finance"

interface FinancePaymentsTableProps {
  payments: PaymentListItem[]
  onConfirm: (id: string) => void
  onReject: (id: string) => void
  onRefund: (id: string) => void
}

export function FinancePaymentsTable({ payments, onConfirm, onReject, onRefund }: FinancePaymentsTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead className="bg-cocoa-50 text-cocoa-500 text-left">
          <tr>
            <th className="px-3 py-2 font-medium">Student</th>
            <th className="px-3 py-2 font-medium">Fee Type</th>
            <th className="px-3 py-2 font-medium">Amount</th>
            <th className="px-3 py-2 font-medium">Status</th>
            <th className="px-3 py-2 font-medium">Date</th>
            <th className="px-3 py-2 font-medium">Actions</th>
          </tr>
        </thead>
        <tbody>
          {payments.map((payment) => (
            <tr key={payment.id} className="border-t border-cocoa-50">
              <td className="px-3 py-2 text-cocoa-700">{payment.student_id || payment.applicant_id || "—"}</td>
              <td className="px-3 py-2 capitalize">{payment.fee_type}</td>
              <td className="px-3 py-2 font-mono">GHS {payment.amount.toFixed(2)}</td>
              <td className="px-3 py-2"><Badge variant={statusToVariant(payment.status)}>{payment.status}</Badge></td>
              <td className="px-3 py-2 text-cocoa-400">{payment.payment_date ? new Date(payment.payment_date).toLocaleDateString() : "—"}</td>
              <td className="px-3 py-2 space-x-2">
                {payment.status === "pending" && (
                  <Button size="xs" onClick={() => onConfirm(payment.id)}>Confirm</Button>
                )}
                {payment.status === "pending" && (
                  <Button size="xs" variant="secondary" onClick={() => onReject(payment.id)}>Reject</Button>
                )}
                {payment.status === "success" && (
                  <Button size="xs" variant="ghost" onClick={() => onRefund(payment.id)}>Refund</Button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
