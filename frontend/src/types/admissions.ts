export type ApplicationStatus =
  | "draft"
  | "submitted"
  | "awaiting_results"
  | "results_uploaded"
  | "results_approved"
  | "eligible"
  | "ineligible"
  | "ranked"
  | "allocated"
  | "waitlisted"
  | "offered"
  | "accepted"
  | "rejected"

export interface ProgrammeChoice {
  programme_id: string
  choice_order: number
}

export interface Applicant {
  id: string
  first_name: string
  last_name: string
  phone: string
  status: ApplicationStatus
  index_number: string | null
  exam_year: number | null
  results: Record<string, string>
  aggregate: number | null
  is_eligible: boolean
  programme_choices: ProgrammeChoice[]
  merit_score: number | null
  merit_rank: number | null
  allocated_programme_id: string | null
  student_id: string | null
  created_at: string
}

export interface CreateApplicantRequest {
  first_name: string
  last_name: string
  phone: string
  date_of_birth?: string
  gender?: string
  address?: string
  region?: string
}

export interface SubmitApplicationRequest {
  index_number: string
  exam_year: number
  exam_type: string
  programme_choices: ProgrammeChoice[]
}

export interface SubmitResultsRequest {
  results: Record<string, string>
}

export const WASSCE_GRADES = ["A1", "B2", "B3", "C4", "C5", "C6", "D7", "D8", "E", "F"] as const

export const CORE_SUBJECTS = [
  "english",
  "mathematics",
  "science",
  "social_studies",
] as const

export interface RankingResultItem {
  applicant_id: string
  merit_score: number
  merit_rank: number
  aggregate: number | null
}

export interface AllocationSummary {
  total_processed: number
  allocated: number
  waitlisted: number
}

export interface WaitlistItem {
  id: string
  first_name: string
  last_name: string
  merit_rank: number | null
  allocated_programme_id: string | null
  created_at: string
}

export interface ProgramCapacity {
  programme_id: string
  capacity_planned: number
  capacity_current: number
  capacity_reserved: number
  available: number
}
