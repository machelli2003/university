import { apiClient } from "./client"

export const studentApi = {
  /** Full dashboard data for the logged-in student */
  me: () => apiClient.get("/students/me"),

  /** Transcripts for a specific student (admin use) */
  transcripts: (studentId: string) => apiClient.get(`/students/${studentId}/transcripts`),

  /** Student's weekly timetable */
  timetable: () => apiClient.get("/students/me/timetable"),

  /** Student's exam results (all semesters) */
  results: () => apiClient.get("/students/me/results"),

  /** Academic standing summary */
  academicStanding: () => apiClient.get("/students/me/academic-standing"),
}
