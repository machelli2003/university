import { useMutation, useQuery } from "@tanstack/react-query"
import { academicApi } from "@/services/api/academic"
import type { RegisterCoursesRequest } from "@/types/registration"

export function useFaculties() {
  return useQuery({
    queryKey: ["faculties"],
    queryFn: () => academicApi.listFaculties(),
  })
}

export function useCourses() {
  return useQuery({
    queryKey: ["courses"],
    queryFn: () => academicApi.listCourses(),
  })
}

export function useRegisterCourses() {
  return useMutation({
    mutationFn: (data: RegisterCoursesRequest) => academicApi.registerCourses(data),
  })
}
