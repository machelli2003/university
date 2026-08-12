export interface SubmitGradeRequest {
  student_id: string
  course_id: string
  academic_year: string
  semester: string
  continuous_assessment: number
  practical_score?: number
  mid_semester_score?: number
  final_exam_score: number
}

export interface GradeResponse {
  grade_id: string
  total_score: number
  letter_grade: string
  status: string
}

export interface PendingGrade {
  id: string
  student_id: string
  course_id: string
  total_score: number
  letter_grade: string
  status: string
  submitted_date?: string
  approved_date?: string
}
