import { useMutation, useQuery } from "@tanstack/react-query"
import { alumniApi } from "@/services/api/alumni"
import type { CreateAlumniProfileRequest, RequestMentorshipRequest, MakeDonationRequest } from "@/types/alumni"

export function useCreateAlumniProfile() {
  return useMutation({
    mutationFn: (data: CreateAlumniProfileRequest) => alumniApi.createProfile(data),
  })
}

export function useAlumniDirectory(graduationYear?: number) {
  return useQuery({
    queryKey: ["alumni-directory", graduationYear],
    queryFn: () => alumniApi.getDirectory(graduationYear),
  })
}

export function useRequestMentorship() {
  return useMutation({
    mutationFn: (data: RequestMentorshipRequest) => alumniApi.requestMentorship(data),
  })
}

export function useMakeDonation() {
  return useMutation({
    mutationFn: (data: MakeDonationRequest) => alumniApi.makeDonation(data),
  })
}
