import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { examApi } from "@/services/api/exam"
import type { SubmitGradeRequest } from "@/types/exam"

export function useSubmitGrade() {
  return useMutation({
    mutationFn: (data: SubmitGradeRequest) => examApi.submitGrade(data),
  })
}

export function usePendingGrades() {
  return useQuery({
    queryKey: ["grades", "pending"],
    queryFn: () => examApi.getPendingGrades(),
  })
}

export function useApproveGrade() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (gradeId: string) => examApi.approveGrade(gradeId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["grades", "pending"] }),
  })
}

export function useMyGrades() {
  return useQuery({
    queryKey: ["grades", "mine"],
    queryFn: () => examApi.getMyGrades(),
  })
}
