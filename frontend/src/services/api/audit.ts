import { apiClient } from "./client"
import type { AuditSummary, AuditList } from "@/types/audit"

export const auditApi = {
  getAuditSummary: async (tenantId?: string): Promise<AuditSummary> => {
    const res = await apiClient.get("/finance/audit/summary", {
      params: tenantId ? { tenant_id: tenantId } : undefined,
    })
    return res.data
  },

  listAudits: async (params: Record<string, any>): Promise<AuditList> => {
    const res = await apiClient.get("/finance/audit", { params })
    return res.data
  },

  exportAudits: async (params: Record<string, any>) => {
    const res = await apiClient.get("/finance/audit/export", { params, responseType: "blob" })
    return res.data
  },
  startExport: async (params: Record<string, any>) => {
    const res = await apiClient.post("/finance/audit/export", params)
    return res.data
  },
  getExportStatus: async (jobId: string) => {
    const res = await apiClient.get(`/finance/audit/export/status/${jobId}`)
    return res.data
  },
  downloadExport: async (jobId: string) => {
    const res = await apiClient.get(`/finance/audit/export/download/${jobId}`, { responseType: "blob" })
    return res.data
  },
}
