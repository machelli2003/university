import { apiClient } from "./client"
import type { UniversityApplication, CreateUniversityApplicationRequest } from "@/types/onboarding"

export const onboardingApi = {
  listApplications: async (status?: string): Promise<UniversityApplication[]> => {
    const res = await apiClient.get("/onboarding/applications", {
      params: status ? { status } : {},
    })
    return res.data
  },

  createApplication: async (data: CreateUniversityApplicationRequest): Promise<UniversityApplication> => {
    const res = await apiClient.post("/onboarding/applications", data)
    return res.data
  },
}
