import { useMutation, useQuery } from "@tanstack/react-query"
import { lecturerApi } from "@/services/api/lecturer"

export function useLecturerMaterials(courseId: string) {
  return useQuery({
    queryKey: ["lecturer", courseId, "materials"],
    queryFn: () => lecturerApi.getMaterials(courseId),
    enabled: Boolean(courseId),
  })
}

export function useUploadMaterial() {
  return useMutation({
    mutationFn: ({ courseId, formData }: { courseId: string; formData: FormData }) =>
      lecturerApi.uploadMaterial(courseId, formData),
  })
}
