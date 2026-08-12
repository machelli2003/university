import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { accommodationApi } from "@/services/api/accommodation"
import type { AllocateRoomRequest, MaintenanceRequestCreate } from "@/types/accommodation"

export function useHalls() {
  return useQuery({
    queryKey: ["halls"],
    queryFn: () => accommodationApi.listHalls(),
  })
}

export function useRooms(hallId: string) {
  return useQuery({
    queryKey: ["rooms", hallId],
    queryFn: () => accommodationApi.listRooms(hallId),
    enabled: !!hallId,
  })
}

export function useAllocateRoom() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: AllocateRoomRequest) => accommodationApi.allocateRoom(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["rooms"] }),
  })
}

export function useReportMaintenance() {
  return useMutation({
    mutationFn: (data: MaintenanceRequestCreate) => accommodationApi.reportMaintenance(data),
  })
}

export function usePendingMaintenance() {
  return useQuery({
    queryKey: ["maintenance", "pending"],
    queryFn: () => accommodationApi.getPendingMaintenance(),
  })
}

export function useOccupancySummary() {
  return useQuery({
    queryKey: ["accommodation", "summary"],
    queryFn: () => accommodationApi.getOccupancySummary(),
  })
}

export function useRoomOccupants(roomId: string) {
  return useQuery({
    queryKey: ["room", roomId, "occupants"],
    queryFn: () => accommodationApi.getRoomOccupants(roomId),
    enabled: !!roomId,
  })
}

export function useDeallocateRoom() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: { student_id: string }) => accommodationApi.deallocateRoom(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["rooms"] }),
  })
}

export function useAssignMaintenance() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, assignee }: { id: string; assignee: string }) => accommodationApi.assignMaintenance(id, assignee),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["maintenance", "pending"] }),
  })
}

export function useResolveMaintenance() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => accommodationApi.resolveMaintenance(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["maintenance", "pending"] }),
  })
}
