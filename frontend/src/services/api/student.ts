import { apiClient } from "./client"

export const studentApi = {
  me: () => apiClient.get("/students/me"),
  transcripts: (studentId: string) => apiClient.get(`/students/${studentId}/transcripts`),
}
