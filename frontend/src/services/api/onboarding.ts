import { apiClient } from "./client"

export interface UniversityApplicationResponse {
  id: string
  university_application_id: string
  legal_name?: string
  display_name?: string
  school_code?: string
  status: string
  requested_by?: string
  admin_first_name?: string
  admin_last_name?: string
  admin_email?: string
  official_email?: string
  official_phone?: string
  country?: string
  timezone?: string
  submitted_at?: string
  approved_at?: string
  activated_at?: string
  tenant_id?: string
  setup_sections: Record<string, boolean>
  university_information?: {
    legal_name?: string
    display_name?: string
    school_code?: string
    official_email?: string
    official_phone?: string
    country?: string
    timezone?: string
    description?: string
    [key: string]: any
  }
  created_at?: string
  updated_at?: string
}

export interface CreateUniversityApplicationRequest {
  legal_name: string
  display_name?: string
  school_code: string
  admin_first_name: string
  admin_last_name: string
  admin_email: string
  institution_type?: string
  is_public?: boolean
  location?: string
  region?: string
  country?: string
  postal_address?: string
  official_email?: string
  official_phone?: string
  website?: string
  logo_url?: string
  favicon_url?: string
  description?: string
  academic_calendar_type?: string
  timezone?: string
  currency?: string
}

export const onboardingApi = {
  // List all university applications
  listApplications: async (status?: string): Promise<UniversityApplicationResponse[]> => {
    const params = status ? `?status=${status}` : ""
    const res = await apiClient.get(`/onboarding/applications${params}`)
    const payload = res.data
    if (Array.isArray(payload)) return payload
    if (payload && Array.isArray((payload as any).items)) return (payload as any).items
    if (payload && Array.isArray((payload as any).data)) return (payload as any).data
    return []
  },

  // Create a new university application (super admin)
  createApplication: async (data: CreateUniversityApplicationRequest): Promise<UniversityApplicationResponse> => {
    const res = await apiClient.post("/onboarding/applications", data)
    return res.data
  },

  // Get a specific university application
  getApplication: async (applicationId: string): Promise<UniversityApplicationResponse> => {
    const res = await apiClient.get(`/onboarding/applications/${applicationId}`)
    return res.data
  },

  // Generic wizard updater for all configured sections
  updateWizardSection: async (
    applicationId: string,
    section: string,
    data: Record<string, any>
  ): Promise<UniversityApplicationResponse> => {
    const routeMap: Record<string, string> = {
      university_information: `/onboarding/applications/${applicationId}/wizard/university-information`,
      id_configuration: `/onboarding/applications/${applicationId}/wizard/id-configuration`,
      academic_years: `/onboarding/applications/${applicationId}/wizard/academic-years`,
      faculties: `/onboarding/applications/${applicationId}/wizard/faculties`,
      departments: `/onboarding/applications/${applicationId}/wizard/departments`,
      programmes: `/onboarding/applications/${applicationId}/wizard/programmes`,
      courses: `/onboarding/applications/${applicationId}/wizard/courses`,
      admission_cycle: `/onboarding/applications/${applicationId}/wizard/admission-cycle`,
      admission_categories: `/onboarding/applications/${applicationId}/wizard/admission-categories`,
      admission_requirements: `/onboarding/applications/${applicationId}/wizard/admission-requirements`,
      application_form: `/onboarding/applications/${applicationId}/wizard/application-form`,
      application_fee: `/onboarding/applications/${applicationId}/wizard/application-fee`,
      staff: `/onboarding/applications/${applicationId}/wizard/staff`,
      student_id_configuration: `/onboarding/applications/${applicationId}/wizard/student-id-configuration`,
      staff_id_configuration: `/onboarding/applications/${applicationId}/wizard/staff-id-configuration`,
      applicant_id_configuration: `/onboarding/applications/${applicationId}/wizard/applicant-id-configuration`,
      finance: `/onboarding/applications/${applicationId}/wizard/finance`,
      grading: `/onboarding/applications/${applicationId}/wizard/grading`,
      graduation: `/onboarding/applications/${applicationId}/wizard/graduation`,
      module_enablement: `/onboarding/applications/${applicationId}/wizard/module-enablement`,
      role_permission: `/onboarding/applications/${applicationId}/wizard/role-permission`,
      hostel: `/onboarding/applications/${applicationId}/wizard/hostel-configuration`,
      library: `/onboarding/applications/${applicationId}/wizard/library-configuration`,
    }

    const route = routeMap[section]
    if (!route) {
      throw new Error(`Unsupported setup section: ${section}`)
    }

    const res = await apiClient.patch(route, data)
    return res.data
  },

  // Update university information
  updateUniversityInformation: async (
    applicationId: string,
    data: Record<string, any>
  ): Promise<UniversityApplicationResponse> => {
    const res = await apiClient.patch(`/onboarding/applications/${applicationId}/wizard/university-information`, data)
    return res.data
  },

  // Submit application for super admin review
  submitForReview: async (applicationId: string): Promise<UniversityApplicationResponse> => {
    const res = await apiClient.post(`/onboarding/applications/${applicationId}/submit`, {})
    return res.data
  },

  // Super admin approves application
  approveApplication: async (applicationId: string): Promise<UniversityApplicationResponse> => {
    const res = await apiClient.post(`/onboarding/applications/${applicationId}/approve`, {})
    return res.data
  },

  // Super admin rejects application
  rejectApplication: async (
    applicationId: string,
    reason: string
  ): Promise<UniversityApplicationResponse> => {
    const res = await apiClient.post(`/onboarding/applications/${applicationId}/reject`, { reason })
    return res.data
  },

  // Request changes to application
  requestChanges: async (
    applicationId: string,
    reason: string
  ): Promise<UniversityApplicationResponse> => {
    const res = await apiClient.post(`/onboarding/applications/${applicationId}/review/request-changes`, {
      reason,
    })
    return res.data
  },

  // Activate approved application (make tenant live)
  activateApplication: async (applicationId: string): Promise<UniversityApplicationResponse> => {
    const res = await apiClient.post(`/onboarding/applications/${applicationId}/activate`, {})
    return res.data
  },

  // Get pending applications for super admin review
  getPendingApplications: async (): Promise<UniversityApplicationResponse[]> => {
    const res = await apiClient.get("/onboarding/applications?status=awaiting_super_admin_approval")
    const payload = res.data
    if (Array.isArray(payload)) return payload
    if (payload && Array.isArray((payload as any).items)) return (payload as any).items
    if (payload && Array.isArray((payload as any).data)) return (payload as any).data
    return []
  },
}
