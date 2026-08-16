import { apiClient } from "./client"
import type { Faculty, Department, Programme, Course } from "@/types/academic"
import type { RegisterCoursesRequest, RegisterCoursesResponse } from "@/types/registration"

export const academicApi = {
  registerCourses: async (data: RegisterCoursesRequest): Promise<RegisterCoursesResponse> => {
    const res = await apiClient.post("/academic/registration/register", data)
    return res.data
  },

  createFaculty: async (data: { name: string; code: string; description?: string }) => {
    const res = await apiClient.post("/academic/faculties", data)
    return res.data
  },

  listFaculties: async (): Promise<Faculty[]> => {
    const res = await apiClient.get("/academic/faculties")
    return res.data
  },

  createDepartment: async (data: { faculty_id: string; name: string; code: string }) => {
    const res = await apiClient.post("/academic/departments", data)
    return res.data
  },

  listDepartments: async (facultyId: string): Promise<Department[]> => {
    const res = await apiClient.get(`/academic/departments/faculty/${facultyId}`)
    return res.data
  },

  createProgramme: async (data: {
    faculty_id: string
    department_id: string
    name: string
    code: string
    duration_years?: number
    capacity_planned?: number
    required_subjects?: string[]
    minimum_grades?: Record<string, string>
    aggregate_threshold?: number
  }) => {
    const res = await apiClient.post("/academic/programmes", data)
    return res.data
  },

  listProgrammes: async (): Promise<Programme[]> => {
    const res = await apiClient.get("/academic/programmes")
    return res.data
  },

  getProgramme: async (id: string): Promise<Programme> => {
    const res = await apiClient.get(`/academic/programmes/${id}`)
    return res.data
  },

  createCourse: async (data: {
    code: string
    name: string
    description?: string
    credit_hours: number
    course_type?: string
    prerequisites?: string[]
    lecturer_id?: string
  }) => {
    const res = await apiClient.post("/academic/courses", data)
    return res.data
  },

  listCourses: async (): Promise<Course[]> => {
    const res = await apiClient.get("/academic/courses")
    return res.data
  },

  createAcademicCalendar: async (data: {
    academic_year: string
    semester: string
    registration_open?: string
    registration_close?: string
    exam_period_start?: string
    exam_period_end?: string
  }) => {
    const res = await apiClient.post("/academic/calendar", data)
    return res.data
  },
}
