import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { counselingApi } from "@/services/api/counseling"

export function useReportCounsel() {
  const qc = useQueryClient()
  return useMutation({ mutationFn: (data: any) => counselingApi.createMessage(data), onSuccess: () => qc.invalidateQueries({ queryKey: ['counseling','student'] }) })
}

export function usePendingCounsel() {
  return useQuery({ queryKey: ['counseling','pending'], queryFn: () => counselingApi.listPending() })
}

export function useReplyCounsel() {
  const qc = useQueryClient()
  return useMutation({ mutationFn: ({ id, response }: any) => counselingApi.reply(id, response), onSuccess: () => qc.invalidateQueries({ queryKey: ['counseling','pending'] }) })
}

export function useStudentCounsel(studentId: string | null) {
  return useQuery({ queryKey: ['counseling','student', studentId], queryFn: () => counselingApi.getForStudent(studentId!), enabled: !!studentId })
}
