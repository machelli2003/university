import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { admissionsApi } from "@/services/api/admissions"
import { academicApi } from "@/services/api/academic"
import type { Applicant, CreateApplicantRequest, SubmitApplicationRequest, SubmitResultsRequest, WaitlistItem, ProgramCapacity } from "@/types/admissions"

const POLLING_STATUS = [
  "submitted",
  "awaiting_results",
  "results_uploaded",
  "results_approved",
  "eligible",
  "ranked",
  "allocated",
]

export function useMyApplication(applicantId: string | undefined) {
  return useQuery<Applicant>({
    queryKey: ["applicant", applicantId],
    queryFn: () => admissionsApi.getApplicant(applicantId!),
    enabled: !!applicantId,
    refetchInterval: applicantId ? 15000 : false,
    refetchOnWindowFocus: true,
  })
}

export function useCreateApplication() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: CreateApplicantRequest) => admissionsApi.createApplication(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["applicant"] }),
  })
}

export function useSubmitApplication(applicantId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: SubmitApplicationRequest) => admissionsApi.submitApplication(applicantId, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["applicant", applicantId] }),
  })
}

export function useSubmitResults(applicantId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: SubmitResultsRequest) => admissionsApi.submitResults(applicantId, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["applicant", applicantId] }),
  })
}

export function useVerifyWAEC(applicantId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (pin: string) => admissionsApi.verifyWAEC(applicantId, pin),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["applicant", applicantId] }),
  })
}

export function useAcceptOffer(applicantId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => admissionsApi.acceptOffer(applicantId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["applicant", applicantId] }),
  })
}

export function useRejectOffer(applicantId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (reason?: string) => admissionsApi.rejectOffer(applicantId, reason),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["applicant", applicantId] }),
  })
}

export function usePendingResults() {
  return useQuery({
    queryKey: ["applicants", "pending-results"],
    queryFn: () => admissionsApi.getPendingResults(),
  })
}

export function useApproveResults() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ applicantId, aggregate }: { applicantId: string; aggregate?: number }) =>
      admissionsApi.approveResults(applicantId, aggregate),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["applicants"] })
      queryClient.invalidateQueries({ queryKey: ["applicants", "pending-results"] })
    },
  })
}

export function useRejectResults() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ applicantId, reason }: { applicantId: string; reason: string }) =>
      admissionsApi.rejectResults(applicantId, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["applicants"] })
      queryClient.invalidateQueries({ queryKey: ["applicants", "pending-results"] })
    },
  })
}

export function useAllApplicants(statusFilter?: string) {
  return useQuery({
    queryKey: ["applicants", "all", statusFilter],
    queryFn: () => admissionsApi.listApplicants(statusFilter),
  })
}

export function useBulkEvaluateEligibility() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => admissionsApi.bulkEvaluateEligibility(),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["applicants"] }),
  })
}

export function useAllocateProgrammes() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => admissionsApi.allocateProgrammes(),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["applicants"] }),
  })
}

export function usePublishOffers() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => admissionsApi.publishOffers(),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["applicants"] }),
  })
}

export function useProcessAdmissions() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => admissionsApi.processAdmissions(),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["applicants"] }),
  })
}

export function useProgrammes() {
  return useQuery({
    queryKey: ["programmes"],
    queryFn: () => academicApi.listProgrammes(),
  })
}

export function useOverrideApplicant(applicantId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: { merit_score?: number; is_eligible?: boolean; eligibility_reason?: string }) => admissionsApi.overrideApplicant(applicantId, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["applicant", applicantId] }),
  })
}

export function useReopenApplication(applicantId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => admissionsApi.reopenApplication(applicantId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["applicant", applicantId] }),
  })
}

export function useWaitlist(programmeId?: string) {
  return useQuery<WaitlistItem[]>({
    queryKey: ["waitlist", programmeId],
    queryFn: () => admissionsApi.getWaitlist(programmeId),
  })
}

export function usePromoteWaitlist() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: { programme_id: string; count?: number }) => admissionsApi.promoteWaitlist(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["waitlist"] }),
  })
}

export function useProgrammeCapacity(programmeId: string) {
  return useQuery<ProgramCapacity>({
    queryKey: ["programme_capacity", programmeId],
    queryFn: () => admissionsApi.getProgrammeCapacity(programmeId),
    enabled: !!programmeId,
  })
}

export function useNotifyOffer(applicantId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => admissionsApi.notifyOffer(applicantId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["applicant", applicantId] }),
  })
}
