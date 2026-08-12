import { useMutation, useQuery } from "@tanstack/react-query"
import { healthApi } from "@/services/api/health"
import type { CreateHealthRecordRequest, BookAppointmentRequest, CounselingRequest } from "@/types/health"

export function useCreateHealthRecord() {
  return useMutation({
    mutationFn: (data: CreateHealthRecordRequest) => healthApi.createRecord(data),
  })
}

export function useHealthRecord(studentId: string | null) {
  return useQuery({
    queryKey: ["health-record", studentId],
    queryFn: () => healthApi.getRecord(studentId!),
    enabled: !!studentId,
    retry: false,
  })
}

export function useBookAppointment() {
  return useMutation({
    mutationFn: (data: BookAppointmentRequest) => healthApi.bookAppointment(data),
  })
}

export function useRequestCounseling() {
  return useMutation({
    mutationFn: (data: CounselingRequest) => healthApi.requestCounseling(data),
  })
}
