import { apiClient } from "./client"
import type { SubmitGradeRequest, GradeResponse, PendingGrade } from "@/types/exam"

export const examApi = {
  submitGrade: async (data: SubmitGradeRequest): Promise<GradeResponse> => {
    const res = await apiClient.post("/exam/grades/submit", data)
    return res.data
  },

  approveGrade: async (gradeId: string) => {
    const res = await apiClient.post(`/exam/grades/${gradeId}/approve`)
    return res.data
  },

  getMyGrades: async (): Promise<PendingGrade[]> => {
    const res = await apiClient.get("/exam/grades/mine")
    return res.data
  },

  getPendingGrades: async (): Promise<PendingGrade[]> => {
    const res = await apiClient.get("/exam/grades/pending")
    return res.data
  },
}
