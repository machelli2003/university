import { apiClient } from "./client"
import type { HealthRecord, CreateHealthRecordRequest, BookAppointmentRequest, CounselingRequest } from "@/types/health"

export const healthApi = {
  createRecord: async (data: CreateHealthRecordRequest) => {
    const res = await apiClient.post("/health-services/records", data)
    return res.data
  },

  getRecord: async (studentId: string): Promise<HealthRecord> => {
    const res = await apiClient.get(`/health-services/records/${studentId}`)
    return res.data
  },

  bookAppointment: async (data: BookAppointmentRequest) => {
    const res = await apiClient.post("/health-services/appointments", data)
    return res.data
  },

  requestCounseling: async (data: CounselingRequest) => {
    const res = await apiClient.post("/health-services/counseling/request", data)
    return res.data
  },
}
