import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { hrApi } from "@/services/api/hr"
import type { LeaveRequest } from "@/types/hr"

export function useRequestLeave() {
  return useMutation({
    mutationFn: (data: LeaveRequest) => hrApi.requestLeave(data),
  })
}

export function usePendingLeaves() {
  return useQuery({
    queryKey: ["leaves", "pending"],
    queryFn: () => hrApi.getPendingLeaves(),
  })
}

export function useApproveLeave() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (leaveId: string) => hrApi.approveLeave(leaveId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["leaves", "pending"] }),
  })
}

export function useRejectLeave() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (leaveId: string) => hrApi.rejectLeave(leaveId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["leaves", "pending"] }),
  })
}
