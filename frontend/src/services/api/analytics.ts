import { apiClient } from "./client"
import type { AdmissionsSummary, EnrollmentSummary, FinanceSummary } from "@/types/analytics"

export const analyticsApi = {
  getAdmissionsSummary: async (tenantId?: string): Promise<AdmissionsSummary> => {
    const res = await apiClient.get("/analytics/admissions/summary", {
      params: tenantId ? { tenant_id: tenantId } : undefined,
    })
    return res.data
  },

  getEnrollmentSummary: async (tenantId?: string): Promise<EnrollmentSummary> => {
    const res = await apiClient.get("/analytics/enrollment/summary", {
      params: tenantId ? { tenant_id: tenantId } : undefined,
    })
    return res.data
  },

  getFinanceSummary: async (tenantId?: string): Promise<FinanceSummary> => {
    const res = await apiClient.get("/analytics/finance/summary", {
      params: tenantId ? { tenant_id: tenantId } : undefined,
    })
    return res.data
  },
}
