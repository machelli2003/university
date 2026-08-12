import { apiClient } from "./client"
import type { CreateProposalRequest, ProposalItem, CreateGrantRequest, CreatePublicationRequest, PublicationItem } from "@/types/research"

export const researchApi = {
  createProposal: async (data: CreateProposalRequest) => {
    const res = await apiClient.post("/research/proposals", data)
    return res.data
  },

  getPendingProposals: async (): Promise<ProposalItem[]> => {
    const res = await apiClient.get("/research/proposals/pending")
    return res.data
  },

  approveProposal: async (proposalId: string) => {
    const res = await apiClient.post(`/research/proposals/${proposalId}/approve`)
    return res.data
  },

  createGrant: async (data: CreateGrantRequest) => {
    const res = await apiClient.post("/research/grants", data)
    return res.data
  },

  addPublication: async (data: CreatePublicationRequest) => {
    const res = await apiClient.post("/research/publications", data)
    return res.data
  },

  getMyPublications: async (): Promise<PublicationItem[]> => {
    const res = await apiClient.get("/research/my-publications")
    return res.data
  },
}
