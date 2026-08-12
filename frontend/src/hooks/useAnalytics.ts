import { useQuery } from "@tanstack/react-query"
import { analyticsApi } from "@/services/api/analytics"
import { useAuthStore } from "@/store/authStore"

export function useAdmissionsSummary() {
  const selectedTenantId = useAuthStore((s) => s.selectedTenantId)

  return useQuery({
    queryKey: ["analytics", "admissions", selectedTenantId],
    queryFn: () => analyticsApi.getAdmissionsSummary(selectedTenantId ?? undefined),
  })
}

export function useEnrollmentSummary() {
  const selectedTenantId = useAuthStore((s) => s.selectedTenantId)

  return useQuery({
    queryKey: ["analytics", "enrollment", selectedTenantId],
    queryFn: () => analyticsApi.getEnrollmentSummary(selectedTenantId ?? undefined),
  })
}

export function useFinanceSummary() {
  const selectedTenantId = useAuthStore((s) => s.selectedTenantId)

  return useQuery({
    queryKey: ["analytics", "finance", selectedTenantId],
    queryFn: () => analyticsApi.getFinanceSummary(selectedTenantId ?? undefined),
  })
}
