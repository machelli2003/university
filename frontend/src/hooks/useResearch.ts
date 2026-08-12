import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { researchApi } from "@/services/api/research"
import type { CreateProposalRequest, CreateGrantRequest, CreatePublicationRequest } from "@/types/research"

export function useCreateProposal() {
  return useMutation({
    mutationFn: (data: CreateProposalRequest) => researchApi.createProposal(data),
  })
}

export function usePendingProposals() {
  return useQuery({
    queryKey: ["proposals", "pending"],
    queryFn: () => researchApi.getPendingProposals(),
  })
}

export function useApproveProposal() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (proposalId: string) => researchApi.approveProposal(proposalId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["proposals", "pending"] }),
  })
}

export function useCreateGrant() {
  return useMutation({
    mutationFn: (data: CreateGrantRequest) => researchApi.createGrant(data),
  })
}

export function useAddPublication() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: CreatePublicationRequest) => researchApi.addPublication(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["my-publications"] }),
  })
}

export function useMyPublications() {
  return useQuery({
    queryKey: ["my-publications"],
    queryFn: () => researchApi.getMyPublications(),
  })
}
