import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { parentsApi } from "@/services/api/parents"

export function useLinkStudent() {
  const qc = useQueryClient()
  return useMutation({ mutationFn: (studentId: string) => parentsApi.linkStudent(studentId), onSuccess: () => qc.invalidateQueries({ queryKey: ['parents','students'] }) })
}

export function useLinkedStudents() {
  return useQuery({ queryKey: ['parents','students'], queryFn: () => parentsApi.listLinkedStudents() })
}
