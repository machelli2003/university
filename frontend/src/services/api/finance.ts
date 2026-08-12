import { apiClient } from "./client"
import type { InitiatePaymentRequest, PaymentHistoryItem } from "@/types/academic"
import type {
  FeeStructureCreateRequest,
  FeeStructureResponse,
  ScholarshipRequest,
  ScholarshipResponse,
  PaymentListItem,
  BalanceResponse,
  ClearanceResponse,
} from "@/types/finance"

export const financeApi = {
  initiatePayment: async (data: InitiatePaymentRequest) => {
    const res = await apiClient.post("/finance/payments/initiate", data)
    return res.data as { payment_id: string; payment_reference: string; authorization_url: string }
  },

  verifyPayment: async (reference: string) => {
    const res = await apiClient.get(`/finance/payments/verify/${reference}`)
    return res.data
  },

  getPaymentHistory: async (studentId: string): Promise<PaymentHistoryItem[]> => {
    const res = await apiClient.get(`/finance/payments/student/${studentId}`)
    return res.data
  },

  listPayments: async (filters: {
    student_id?: string
    status?: string
    fee_type?: string
    start_date?: string
    end_date?: string
  }): Promise<PaymentListItem[]> => {
    const res = await apiClient.get("/finance/payments", { params: filters })
    return res.data
  },

  confirmPayment: async (paymentId: string) => {
    const res = await apiClient.post(`/finance/payments/${paymentId}/confirm`)
    return res.data as { payment_id: string; payment_reference: string; amount: number; status: string }
  },

  rejectPayment: async (paymentId: string, reason?: string) => {
    const res = await apiClient.post(`/finance/payments/${paymentId}/reject`, null, { params: { reason } })
    return res.data as { payment_id: string; payment_reference: string; amount: number; status: string }
  },

  refundPayment: async (paymentId: string) => {
    const res = await apiClient.post(`/finance/payments/${paymentId}/refund`)
    return res.data as { payment_id: string; payment_reference: string; amount: number; status: string }
  },

  getBalance: async (studentId: string, academicYear?: string): Promise<BalanceResponse> => {
    const res = await apiClient.get(`/finance/balance/${studentId}`, {
      params: academicYear ? { academic_year: academicYear } : undefined,
    })
    return res.data
  },

  getClearance: async (studentId: string, academicYear?: string): Promise<ClearanceResponse> => {
    const res = await apiClient.get(`/finance/clearance/${studentId}`, {
      params: academicYear ? { academic_year: academicYear } : undefined,
    })
    return res.data
  },

  listFeeStructures: async (): Promise<FeeStructureResponse[]> => {
    const res = await apiClient.get("/finance/structures")
    return res.data
  },

  listScholarships: async (): Promise<ScholarshipResponse[]> => {
    const res = await apiClient.get("/finance/scholarships")
    return res.data
  },

  createFeeStructure: async (data: FeeStructureCreateRequest): Promise<FeeStructureResponse> => {
    const res = await apiClient.post("/finance/structures", data)
    return res.data
  },

  createScholarship: async (data: ScholarshipRequest): Promise<ScholarshipResponse> => {
    const res = await apiClient.post("/finance/scholarships", data)
    return res.data
  },
}
