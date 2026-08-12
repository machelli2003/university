import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { financeApi } from "@/services/api/finance"
import type { InitiatePaymentRequest } from "@/types/academic"
import type { FeeStructureCreateRequest, ScholarshipRequest } from "@/types/finance"
import type { PaymentListItem, BalanceResponse, ClearanceResponse } from "@/types/finance"

export function useInitiatePayment() {
  return useMutation({
    mutationFn: (data: InitiatePaymentRequest) => financeApi.initiatePayment(data),
  })
}

export function useVerifyPayment(reference: string | null) {
  return useQuery({
    queryKey: ["payment-verify", reference],
    queryFn: () => financeApi.verifyPayment(reference!),
    enabled: !!reference,
  })
}

export function usePaymentHistory(studentId: string | null) {
  return useQuery({
    queryKey: ["payment-history", studentId],
    queryFn: () => financeApi.getPaymentHistory(studentId!),
    enabled: !!studentId,
  })
}

export function usePayments(filters: {
  student_id?: string
  status?: string
  fee_type?: string
  start_date?: string
  end_date?: string
}) {
  return useQuery<PaymentListItem[]>({
    queryKey: ["payments", filters],
    queryFn: () => financeApi.listPayments(filters),
    enabled: true,
  })
}

export function useConfirmPayment() {
  return useMutation({
    mutationFn: (paymentId: string) => financeApi.confirmPayment(paymentId),
  })
}

export function useRejectPayment() {
  return useMutation({
    mutationFn: ({ paymentId, reason }: { paymentId: string; reason?: string }) =>
      financeApi.rejectPayment(paymentId, reason),
  })
}

export function useRefundPayment() {
  return useMutation({
    mutationFn: (paymentId: string) => financeApi.refundPayment(paymentId),
  })
}

export function useStudentBalance(studentId: string | null, academicYear?: string) {
  return useQuery<BalanceResponse>({
    queryKey: ["balance", studentId, academicYear],
    queryFn: () => financeApi.getBalance(studentId!, academicYear),
    enabled: !!studentId,
  })
}

export function useStudentClearance(studentId: string | null, academicYear?: string) {
  return useQuery<ClearanceResponse>({
    queryKey: ["clearance", studentId, academicYear],
    queryFn: () => financeApi.getClearance(studentId!, academicYear),
    enabled: !!studentId,
  })
}

export function useFeeStructures() {
  return useQuery({
    queryKey: ["fee-structures"],
    queryFn: financeApi.listFeeStructures,
  })
}

export function useScholarships() {
  return useQuery({
    queryKey: ["scholarships"],
    queryFn: financeApi.listScholarships,
  })
}

export function useCreateFeeStructure() {
  const queryClient = useQueryClient()
  return useMutation<any, Error, FeeStructureCreateRequest>({
    mutationFn: (data) => financeApi.createFeeStructure(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["fee-structures"] }),
  })
}

export function useCreateScholarship() {
  const queryClient = useQueryClient()
  return useMutation<any, Error, ScholarshipRequest>({
    mutationFn: (data) => financeApi.createScholarship(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["scholarships"] }),
  })
}
