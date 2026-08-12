import { apiClient } from "./client"
import type { Tenant, TenantCreateRequest, TenantUpdateRequest } from "@/types/tenant"

export const tenantApi = {
  listTenants: async (includeInactive = false): Promise<Tenant[]> => {
    const res = await apiClient.get("/finance/tenants", {
      params: { include_inactive: includeInactive },
    })
    return res.data
  },

  getTenant: async (tenantId: string): Promise<Tenant> => {
    const res = await apiClient.get(`/finance/tenants/${tenantId}`)
    return res.data
  },

  createTenant: async (data: TenantCreateRequest): Promise<Tenant> => {
    const res = await apiClient.post("/finance/tenants", data)
    return res.data
  },

  updateTenant: async (tenantId: string, data: Partial<TenantUpdateRequest>): Promise<Tenant> => {
    const res = await apiClient.put(`/finance/tenants/${tenantId}`, data)
    return res.data
  },

  activateTenant: async (tenantId: string): Promise<Tenant> => {
    const res = await apiClient.patch(`/finance/tenants/${tenantId}/activate`)
    return res.data
  },

  deactivateTenant: async (tenantId: string): Promise<Tenant> => {
    const res = await apiClient.patch(`/finance/tenants/${tenantId}/deactivate`)
    return res.data
  },
}
