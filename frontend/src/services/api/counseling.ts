import { apiClient } from "./client"
import type { CounselingItem } from "@/types/counseling"

export const counselingApi = {
  createMessage: async (data: { student_id: string; subject: string; message: string }) => {
    const res = await apiClient.post('/counseling', data)
    return res.data
  },

  listPending: async (): Promise<CounselingItem[]> => {
    const res = await apiClient.get('/counseling/pending')
    return res.data
  },

  reply: async (id: string, response: string) => {
    const res = await apiClient.post(`/counseling/${id}/reply`, { response })
    return res.data
  },

  getForStudent: async (studentId: string): Promise<CounselingItem[]> => {
    const res = await apiClient.get(`/counseling/student/${studentId}`)
    return res.data
  },
}
