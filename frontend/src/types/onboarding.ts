export interface UniversityApplication {
  id: string
  university_application_id: string
  legal_name: string
  display_name?: string
  school_code: string
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
  status: string
  requested_by?: string
  admin_first_name?: string
  admin_last_name?: string
  admin_email?: string
  review_notes?: string
  review_requested_at?: string
  submitted_at?: string
  approved_at?: string
  rejected_at?: string
  provisioned_at?: string
  activated_at?: string
  tenant_id?: string
  setup_sections: Record<string, boolean>
  created_at: string
  updated_at: string
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

export interface UpdateUniversityApplicationRequest {
  display_name?: string
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
  review_notes?: string
}
