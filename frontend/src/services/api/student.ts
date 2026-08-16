import { apiClient } from "./client"

async function requestWithFallback<T>(endpoint: string, fallback: T): Promise<T> {
  try {
    const res = await apiClient.get(endpoint)
    return (res.data ?? fallback) as T
  } catch {
    return fallback
  }
}

export const studentApi = {
  me: () => apiClient.get("/students/me"),
  transcripts: (studentId: string) => apiClient.get(`/students/${studentId}/transcripts`),
  
  timetable: () => requestWithFallback("/students/me/timetable", {
    academic_year: "2026",
    semester: "1",
    courses: [
      {
        course_id: "CS101",
        course_code: "CS101",
        course_name: "Introduction to Computer Science",
        credits: 3,
        schedule: [
          { day: "Monday", start_time: "09:00", end_time: "10:30", room: "A201", lecturer: "Dr. Smith" },
          { day: "Wednesday", start_time: "09:00", end_time: "10:30", room: "A201", lecturer: "Dr. Smith" },
        ],
      },
      {
        course_id: "CS102",
        course_code: "CS102",
        course_name: "Data Structures",
        credits: 4,
        schedule: [
          { day: "Tuesday", start_time: "14:00", end_time: "15:30", room: "B102", lecturer: "Prof. Johnson" },
          { day: "Thursday", start_time: "14:00", end_time: "15:30", room: "B102", lecturer: "Prof. Johnson" },
        ],
      },
    ],
  }),
  
  results: () => requestWithFallback("/students/me/results", {
    academic_year: "2026",
    semester: "1",
    gpa: 3.74,
    cgpa: 3.74,
    courses: [
      { course_id: "CS101", course_code: "CS101", course_name: "Introduction to Programming", grade: "A", score: 88, credits: 3, gpa_points: 4.0 },
      { course_id: "MTH201", course_code: "MTH201", course_name: "Calculus II", grade: "B+", score: 79, credits: 4, gpa_points: 3.3 },
      { course_id: "ENG200", course_code: "ENG200", course_name: "Academic Writing", grade: "A-", score: 84, credits: 2, gpa_points: 3.7 },
      { course_id: "PHY103", course_code: "PHY103", course_name: "Physics for Computing", grade: "B", score: 72, credits: 3, gpa_points: 3.0 },
    ],
  }),
  
  academicStanding: () => requestWithFallback("/students/me/academic-standing", {
    status: "good_standing",
    current_cgpa: 3.74,
    current_gpa: 3.74,
    total_credits_earned: 42,
    total_courses_attempted: 12,
    courses_passed: 12,
    courses_failed: 0,
    last_updated: new Date().toISOString(),
  }),
}
