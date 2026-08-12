import { apiClient } from "./client"

export const parentsApi = {
  linkStudent: async (studentId: string) => {
    const res = await apiClient.post('/parents/link', { student_id: studentId })
    return res.data
  },

  listLinkedStudents: async () => {
    const res = await apiClient.get('/parents/students')
    return res.data
  }
}
