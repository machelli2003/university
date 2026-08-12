export interface RegisterCoursesRequest {
  student_id: string
  course_ids: string[]
  academic_year: string
  semester: string
}

export interface RegisterCoursesResponse {
  student_id: string
  registered_courses: string[]
  total_credits: number
  academic_year: string
  semester: string
  status: string
}
