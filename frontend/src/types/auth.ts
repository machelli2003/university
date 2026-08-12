export type UserRole =
  | "super_admin"
  | "university_admin"
  | "registrar"
  | "admissions_officer"
  | "dean"
  | "head_of_department"
  | "finance_officer"
  | "hostel_administrator"
  | "librarian"
  | "lecturer"
  | "student"
  | "applicant"
  | "parent_guardian"
  | "auditor"

export interface User {
  id: string
  tenant_id?: string
  email: string
  first_name: string
  last_name: string
  age?: number
  role: UserRole
  permissions: string[]
  is_active: boolean
  is_verified: boolean
  login_attempts?: number
  locked_until?: string | null
  created_at: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  first_name: string
  last_name: string
  password: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  user: User
}
