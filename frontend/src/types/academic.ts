export interface Faculty {
  id: string
  name: string
  code: string
}

export interface Department {
  id: string
  name: string
  code: string
}

export interface Programme {
  id: string
  name: string
  code: string
  duration_years: number
  capacity_planned: number
  capacity_current: number
}

export interface Course {
  id: string
  code: string
  name: string
  credit_hours: number
  course_type: string
}

export interface PaymentHistoryItem {
  id: string
  amount: number
  fee_type: string
  status: string
  payment_date: string | null
  receipt_number: string | null
}

export interface InitiatePaymentRequest {
  student_id: string
  amount: number
  fee_type: string
  payment_method: "mobile_money" | "bank_transfer" | "card" | "cash"
}
