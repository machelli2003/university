import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { workflowApi } from "@/services/api/workflow"
import type { ApprovalActionRequest } from "@/types/workflow"

export function useMyApprovalTasks() {
  return useQuery({
    queryKey: ["workflow-tasks"],
    queryFn: () => workflowApi.getMyTasks(),
  })
}

export function useProcessApproval() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: ApprovalActionRequest) => workflowApi.processApproval(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["workflow-tasks"] }),
  })
}
