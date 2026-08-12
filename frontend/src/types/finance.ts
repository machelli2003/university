export interface FeeStructureCreateRequest {
  programme_id?: string
  level?: string
  academic_year: string
  fees: Record<string, number>
}

export interface FeeStructureResponse {
  id: string
  programme_id?: string
  level?: string
  academic_year: string
  fees: Record<string, number>
}

export interface ScholarshipRequest {
  student_id: string
  name: string
  scholarship_type: string
  amount: number
  percentage?: number
  start_date: string
  end_date?: string
}

export interface ScholarshipResponse {
  id: string
  student_id: string
  name: string
  scholarship_type: string
  amount: number
  percentage?: number
  start_date: string
  end_date?: string | null
  is_active: boolean
}

export interface PaymentListItem {
  id: string
  tenant_id: string
  student_id?: string | null
  applicant_id?: string | null
  amount: number
  fee_type: string
  academic_year?: string | null
  payment_method: string
  payment_reference: string
  status: string
  paystack_reference?: string | null
  payment_date?: string | null
  receipt_number?: string | null
  created_at: string
}

export interface BalanceResponse {
  total_due: number
  total_paid: number
  total_scholarships: number
  balance: number
}

export interface ClearanceResponse {
  student_id: string
  tenant_id: string
  is_cleared: boolean
  message: string
  balance: number
  pending_payments: number
}
