import { useMutation, useQuery } from "@tanstack/react-query"
import { onboardingApi } from "@/services/api/onboarding"
import type { CreateUniversityApplicationRequest, UniversityApplication } from "@/types/onboarding"

export function useMyUniversityApplications(status?: string) {
  return useQuery<UniversityApplication[]>({
    queryKey: ["onboarding", "applications", status],
    queryFn: () => onboardingApi.listApplications(status),
  })
}

export function useCreateUniversityApplication() {
  return useMutation<UniversityApplication, Error, CreateUniversityApplicationRequest>({
    mutationFn: (data) => onboardingApi.createApplication(data),
  })
}
