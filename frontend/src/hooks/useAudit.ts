import { useQuery } from "@tanstack/react-query"
import { auditApi } from "@/services/api/audit"
import { useAuthStore } from "@/store/authStore"
import type { AuditSummary, AuditList } from "@/types/audit"

export function useAuditSummary() {
  const selectedTenantId = useAuthStore((s) => s.selectedTenantId)

  return useQuery<AuditSummary>({
    queryKey: ["audit-summary", selectedTenantId],
    queryFn: () => auditApi.getAuditSummary(selectedTenantId ?? undefined),
  })
}

export function useAuditList(page: number, pageSize: number, filters: Record<string, any>) {
  const selectedTenantId = useAuthStore((s) => s.selectedTenantId)
  const params = { page, page_size: pageSize, tenant_id: selectedTenantId ?? undefined, ...filters }

  // keepPreviousData can cause typing issues depending on react-query version; omit here for compatibility
  return useQuery<AuditList>({
    queryKey: ["audit-list", params],
    queryFn: () => auditApi.listAudits(params),
  })
}
