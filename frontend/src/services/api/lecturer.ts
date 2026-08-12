import { apiClient } from "./client"

export const lecturerApi = {
  myCourses: () => apiClient.get(`/lecturer/courses`),
  markAttendance: (courseId: string, data: any) => apiClient.post(`/lecturer/courses/${courseId}/attendance`, data),
  getAttendance: (courseId: string, sessionDate?: string) => apiClient.get(`/lecturer/courses/${courseId}/attendance${sessionDate ? `?session_date=${encodeURIComponent(sessionDate)}` : ''}`),
  getRoster: (courseId: string) => apiClient.get(`/lecturer/courses/${courseId}/roster`),
  generateQr: (courseId: string, baseUrl?: string) => apiClient.get(`/lecturer/courses/${courseId}/attendance/qr${baseUrl ? `?base_url=${encodeURIComponent(baseUrl)}` : ''}`),
  getReport: (courseId: string, start: string, end: string) => apiClient.get(`/lecturer/courses/${courseId}/attendance/report?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`),
  uploadMaterial: (courseId: string, formData: FormData) => apiClient.post(`/lecturer/courses/${courseId}/materials`, formData),
  getMaterials: async (courseId: string) => {
    const res = await apiClient.get(`/lecturer/courses/${courseId}/materials`)
    return res.data
  },
}
