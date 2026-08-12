import { apiClient } from "./client"
import type { ApprovalTaskItem, ApprovalActionRequest } from "@/types/workflow"

export const workflowApi = {
  getMyTasks: async (): Promise<ApprovalTaskItem[]> => {
    const res = await apiClient.get("/workflow/my-tasks")
    return res.data
  },

  processApproval: async (data: ApprovalActionRequest) => {
    const res = await apiClient.post("/workflow/approve", data)
    return res.data
  },
}
