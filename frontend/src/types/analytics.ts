export interface AdmissionsSummary {
  total_applications: number
  eligible: number
  pending_verification: number
}

export interface EnrollmentSummary {
  active_students: number
  on_probation: number
}

export interface FinanceSummary {
  revenue_last_30_days: number
  pending_payments: number
}
