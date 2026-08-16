import { useMutation, useQuery } from "@tanstack/react-query"
import { onboardingApi, type UniversityApplicationResponse, type CreateUniversityApplicationRequest } from "@/services/api/onboarding"

export function useMyUniversityApplications(status?: string) {
  return useQuery<UniversityApplicationResponse[]>({
    queryKey: ["onboarding", "applications", status],
    queryFn: () => onboardingApi.listApplications(status),
  })
}

export function useCreateUniversityApplication() {
  return useMutation<UniversityApplicationResponse, Error, CreateUniversityApplicationRequest>({
    mutationFn: (data) => onboardingApi.createApplication(data),
  })
}
