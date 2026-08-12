import { apiClient } from "./client"
import type {
  Applicant,
  CreateApplicantRequest,
  SubmitApplicationRequest,
  SubmitResultsRequest,
  RankingResultItem,
  AllocationSummary,
} from "@/types/admissions"

export const admissionsApi = {
  createApplication: async (data: CreateApplicantRequest): Promise<Applicant> => {
    const res = await apiClient.post("/admissions/apply", data)
    return res.data
  },

  submitApplication: async (applicantId: string, data: SubmitApplicationRequest): Promise<Applicant> => {
    const res = await apiClient.post(`/admissions/${applicantId}/submit`, data)
    return res.data
  },

  submitResults: async (applicantId: string, data: SubmitResultsRequest): Promise<Applicant> => {
    const res = await apiClient.post(`/admissions/${applicantId}/results/submit`, data)
    return res.data
  },

  verifyWAEC: async (applicantId: string, pin: string): Promise<{ verified: boolean; details: any; message: string }> => {
    const res = await apiClient.post(`/admissions/${applicantId}/waec/verify`, { pin })
    return res.data
  },

  getPendingResults: async (): Promise<Applicant[]> => {
    const res = await apiClient.get("/admissions/results/pending")
    return res.data
  },

  approveResults: async (applicantId: string, aggregate?: number): Promise<Applicant> => {
    const res = await apiClient.post(`/admissions/${applicantId}/results/approve`, { aggregate })
    return res.data
  },

  rejectResults: async (applicantId: string, reason: string): Promise<Applicant> => {
    const res = await apiClient.post(`/admissions/${applicantId}/results/reject`, { reason })
    return res.data
  },

  evaluateEligibility: async (applicantId: string) => {
    const res = await apiClient.post(`/admissions/${applicantId}/eligibility/evaluate`)
    return res.data
  },

  bulkEvaluateEligibility: async () => {
    const res = await apiClient.post("/admissions/eligibility/bulk-evaluate")
    return res.data
  },

  rankApplicants: async (programmeId: string): Promise<RankingResultItem[]> => {
    const res = await apiClient.post(`/admissions/programmes/${programmeId}/rank`)
    return res.data
  },

  allocateProgrammes: async (): Promise<AllocationSummary> => {
    const res = await apiClient.post("/admissions/allocate")
    return res.data
  },

  publishOffers: async () => {
    const res = await apiClient.post("/admissions/offers/publish")
    return res.data
  },

  processAdmissions: async (): Promise<{ eligible: number; ineligible: number; ranked: number; allocated: number; waitlisted: number; offers_published: number }> => {
    const res = await apiClient.post("/admissions/process")
    return res.data
  },

  acceptOffer: async (applicantId: string): Promise<Applicant> => {
    const res = await apiClient.post(`/admissions/${applicantId}/offer/accept`)
    return res.data
  },

  rejectOffer: async (applicantId: string, reason?: string): Promise<Applicant> => {
    const res = await apiClient.post(`/admissions/${applicantId}/offer/reject`, { reason })
    return res.data
  },

  getApplicant: async (applicantId: string): Promise<Applicant> => {
    const res = await apiClient.get(`/admissions/${applicantId}`)
    return res.data
  },

  listApplicants: async (statusFilter?: string): Promise<Applicant[]> => {
    const res = await apiClient.get("/admissions/", {
      params: statusFilter ? { status_filter: statusFilter } : {},
    })
    return res.data
  },

  overrideApplicant: async (applicantId: string, data: { merit_score?: number; is_eligible?: boolean; eligibility_reason?: string }) => {
    const res = await apiClient.patch(`/admissions/${applicantId}/override`, data)
    return res.data
  },

  reopenApplication: async (applicantId: string) => {
    const res = await apiClient.post(`/admissions/${applicantId}/reopen`)
    return res.data
  },

  getWaitlist: async (programmeId?: string) => {
    const res = await apiClient.get(`/admissions/waitlist`, { params: programmeId ? { programme_id: programmeId } : {} })
    return res.data
  },

  promoteWaitlist: async (data: { programme_id: string; count?: number }) => {
    const res = await apiClient.post(`/admissions/waitlist/promote`, data)
    return res.data
  },

  getProgrammeCapacity: async (programmeId: string) => {
    const res = await apiClient.get(`/admissions/programmes/${programmeId}/capacity`)
    return res.data
  },

  notifyOffer: async (applicantId: string) => {
    const res = await apiClient.post(`/admissions/offers/notify/${applicantId}`)
    return res.data
  },
}
