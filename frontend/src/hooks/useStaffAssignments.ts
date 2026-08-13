import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/services/api/client"

interface StaffAssignment {
  id: string
  tenant_id: string
  staff_id: string
  assignment_type: string
  resource_id: string
  resource_name: string
  staff_role: string
  permissions: string[]
  is_active: boolean
  assigned_at: string
  updated_at: string
}

interface CreateAssignmentRequest {
  staff_id: string
  assignment_type: string
  resource_id: string
  resource_name: string
  staff_role: string
  permissions: string[]
  start_date: string
  end_date?: string | null
}

interface UpdateAssignmentRequest {
  staff_role?: string
  permissions?: string[]
  is_active?: boolean
  end_date?: string | null
}

/**
 * Hook for managing staff assignments (Section 57)
 */
export function useStaffAssignments() {
  const queryClient = useQueryClient()
  const token = localStorage.getItem("access_token")

  // List all assignments
  const listAssignments = useQuery({
    queryKey: ["staffAssignments"],
    queryFn: async () => {
      const response = await apiClient.get<StaffAssignment[]>("/api/v1/staff-assignments", {
        headers: { Authorization: `Bearer ${token}` },
      })
      return response.data
    },
    enabled: !!token,
  })

  // Get assignments for a specific staff member
  const getStaffAssignments = (staffId: string) =>
    useQuery({
      queryKey: ["staffAssignments", staffId],
      queryFn: async () => {
        const response = await apiClient.get<StaffAssignment[]>(
          `/api/v1/staff-assignments/staff/${staffId}`,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        )
        return response.data
      },
      enabled: !!token && !!staffId,
    })

  // Get single assignment
  const getAssignment = (assignmentId: string) =>
    useQuery({
      queryKey: ["staffAssignments", assignmentId],
      queryFn: async () => {
        const response = await apiClient.get<StaffAssignment>(
          `/api/v1/staff-assignments/${assignmentId}`,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        )
        return response.data
      },
      enabled: !!token && !!assignmentId,
    })

  // Create assignment
  const createAssignment = useMutation({
    mutationFn: async (request: CreateAssignmentRequest) => {
      const response = await apiClient.post<StaffAssignment>(
        "/api/v1/staff-assignments",
        request,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      )
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["staffAssignments"] })
    },
  })

  // Update assignment
  const updateAssignment = useMutation({
    mutationFn: async ({
      assignmentId,
      data,
    }: {
      assignmentId: string
      data: UpdateAssignmentRequest
    }) => {
      const response = await apiClient.put<StaffAssignment>(
        `/api/v1/staff-assignments/${assignmentId}`,
        data,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      )
      return response.data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["staffAssignments"] })
      queryClient.invalidateQueries({ queryKey: ["staffAssignments", variables.assignmentId] })
    },
  })

  // Delete assignment
  const deleteAssignment = useMutation({
    mutationFn: async (assignmentId: string) => {
      await apiClient.delete(`/api/v1/staff-assignments/${assignmentId}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["staffAssignments"] })
    },
  })

  return {
    listAssignments,
    getStaffAssignments,
    getAssignment,
    createAssignment,
    updateAssignment,
    deleteAssignment,
  }
}
