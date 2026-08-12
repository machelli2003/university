import { apiClient } from "./client"
import type { AlumniProfileItem, CreateAlumniProfileRequest, RequestMentorshipRequest, MakeDonationRequest } from "@/types/alumni"

export const alumniApi = {
  createProfile: async (data: CreateAlumniProfileRequest) => {
    const res = await apiClient.post("/alumni/profiles", data)
    return res.data
  },

  getDirectory: async (graduationYear?: number): Promise<AlumniProfileItem[]> => {
    const res = await apiClient.get("/alumni/directory", {
      params: graduationYear ? { graduation_year: graduationYear } : {},
    })
    return res.data
  },

  requestMentorship: async (data: RequestMentorshipRequest) => {
    const res = await apiClient.post("/alumni/mentorship/request", data)
    return res.data
  },

  makeDonation: async (data: MakeDonationRequest) => {
    const res = await apiClient.post("/alumni/donations", data)
    return res.data
  },

  getTotalDonations: async (): Promise<{ total_donations: number }> => {
    const res = await apiClient.get("/alumni/donations/total")
    return res.data
  },
}
