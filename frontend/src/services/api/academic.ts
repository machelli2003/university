import { apiClient } from "./client"
import type { Faculty, Department, Programme, Course } from "@/types/academic"
import type { RegisterCoursesRequest, RegisterCoursesResponse } from "@/types/registration"

export const academicApi = {
  registerCourses: async (data: RegisterCoursesRequest): Promise<RegisterCoursesResponse> => {
    const res = await apiClient.post("/academic/registration/register", data)
    return res.data
  },

  listFaculties: async (): Promise<Faculty[]> => {
    const res = await apiClient.get("/academic/faculties")
    return res.data
  },

  listDepartments: async (facultyId: string): Promise<Department[]> => {
    const res = await apiClient.get(`/academic/departments/faculty/${facultyId}`)
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

  listCourses: async (): Promise<Course[]> => {
    const res = await apiClient.get("/academic/courses")
    return res.data
  },
}
