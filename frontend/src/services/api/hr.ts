import { apiClient } from "./client"
import type { LeaveRequest, LeaveItem } from "@/types/hr"

export const hrApi = {
  requestLeave: async (data: LeaveRequest) => {
    const res = await apiClient.post("/hr/leave/request", data)
    return res.data
  },

  getPendingLeaves: async (): Promise<LeaveItem[]> => {
    const res = await apiClient.get("/hr/leave/pending")
    return res.data
  },

  approveLeave: async (leaveId: string) => {
    const res = await apiClient.post(`/hr/leave/${leaveId}/approve`)
    return res.data
  },

  rejectLeave: async (leaveId: string) => {
    const res = await apiClient.post(`/hr/leave/${leaveId}/reject`)
    return res.data
  },
}
