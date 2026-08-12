export interface Tenant {
  id: string
  name: string
  subdomain: string
  description?: string
  logo_url?: string
  favicon_url?: string
  admin_email: string
  admin_phone?: string
  country: string
  timezone: string
  primary_color?: string
  secondary_color?: string
  accent_color?: string
  subscription_tier: string
  subscription_start: string
  subscription_end?: string
  is_active: boolean
  is_trial: boolean
  features: Record<string, boolean>
}

export interface TenantCreateRequest {
  name: string
  subdomain: string
  description?: string
  logo_url?: string
  favicon_url?: string
  admin_email: string
  admin_phone?: string
  country: string
  timezone: string
  primary_color?: string
  secondary_color?: string
  accent_color?: string
  subscription_tier?: string
  features?: Record<string, boolean>
}

export interface TenantUpdateRequest {
  name?: string
  description?: string
  logo_url?: string
  favicon_url?: string
  admin_email?: string
  admin_phone?: string
  country?: string
  timezone?: string
  primary_color?: string
  secondary_color?: string
  accent_color?: string
  subscription_tier?: string
  subscription_start?: string
  subscription_end?: string
  is_active?: boolean
  is_trial?: boolean
  features?: Record<string, boolean>
}
