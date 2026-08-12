export interface AlumniProfileItem {
  id: string
  current_occupation: string | null
  company: string | null
}

export interface CreateAlumniProfileRequest {
  student_id: string
  graduation_year: number
  current_occupation?: string
  company?: string
  location?: string
}

export interface RequestMentorshipRequest {
  mentor_id: string
}

export interface MakeDonationRequest {
  amount: number
  purpose: string
}
