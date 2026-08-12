import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { tenantApi } from "@/services/api/tenant"
import type { Tenant, TenantCreateRequest } from "@/types/tenant"

export function useTenants(includeInactive = false) {
  return useQuery<Tenant[]>({
    queryKey: ["tenants", includeInactive],
    queryFn: () => tenantApi.listTenants(includeInactive),
  })
}

export function useCreateTenant() {
  const queryClient = useQueryClient()
  return useMutation<Tenant, Error, TenantCreateRequest>({
    mutationFn: (data) => tenantApi.createTenant(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["tenants"] }),
  })
}

export function useUpdateTenant() {
  const queryClient = useQueryClient()
  return useMutation<Tenant, Error, { tenantId: string; data: Partial<TenantCreateRequest> }>({
    mutationFn: ({ tenantId, data }) => tenantApi.updateTenant(tenantId, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["tenants"] }),
  })
}

export function useActivateTenant() {
  const queryClient = useQueryClient()
  return useMutation<Tenant, Error, string>({
    mutationFn: (tenantId) => tenantApi.activateTenant(tenantId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["tenants"] }),
  })
}

export function useDeactivateTenant() {
  const queryClient = useQueryClient()
  return useMutation<Tenant, Error, string>({
    mutationFn: (tenantId) => tenantApi.deactivateTenant(tenantId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["tenants"] }),
  })
}
