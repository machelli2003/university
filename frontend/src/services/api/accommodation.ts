import { apiClient } from "./client"
import type { Hall, Room, AllocateRoomRequest, MaintenanceRequestCreate, MaintenanceRequestItem, OccupancySummaryResponse, RoomOccupantResponse, HousingSelectionRequest, StudentHousingStatusResponse } from "@/types/accommodation"

export const accommodationApi = {
  listHalls: async (): Promise<Hall[]> => {
    const res = await apiClient.get("/accommodation/halls")
    return res.data
  },

  listRooms: async (hallId: string): Promise<Room[]> => {
    const res = await apiClient.get(`/accommodation/rooms/hall/${hallId}`)
    return res.data
  },

  allocateRoom: async (data: AllocateRoomRequest) => {
    const res = await apiClient.post("/accommodation/allocate", data)
    return res.data
  },

  createHall: async (data: { name: string; capacity: number; gender?: string }) => {
    const res = await apiClient.post("/accommodation/halls", data)
    return res.data
  },

  createRoom: async (data: { hall_id: string; room_number: string; room_type: string; capacity: number }) => {
    const res = await apiClient.post("/accommodation/rooms", data)
    return res.data
  },

  reportMaintenance: async (data: MaintenanceRequestCreate) => {
    const res = await apiClient.post("/accommodation/maintenance", data)
    return res.data
  },

  getPendingMaintenance: async (): Promise<MaintenanceRequestItem[]> => {
    const res = await apiClient.get("/accommodation/maintenance/pending")
    return res.data
  },

  getOccupancySummary: async (): Promise<OccupancySummaryResponse> => {
    const res = await apiClient.get("/accommodation/summary")
    return res.data
  },

  getRoomOccupants: async (roomId: string): Promise<RoomOccupantResponse[]> => {
    const res = await apiClient.get(`/accommodation/rooms/${roomId}/occupants`)
    return res.data
  },

  deallocateRoom: async (data: { student_id: string }) => {
    const res = await apiClient.post("/accommodation/deallocate", data)
    return res.data
  },

  assignMaintenance: async (maintenanceId: string, assigneeId: string) => {
    const res = await apiClient.post(`/accommodation/maintenance/${maintenanceId}/assign`, { assignee_id: assigneeId })
    return res.data
  },

  resolveMaintenance: async (maintenanceId: string) => {
    const res = await apiClient.post(`/accommodation/maintenance/${maintenanceId}/resolve`)
    return res.data
  },

  getMyHousing: async (): Promise<StudentHousingStatusResponse> => {
    const res = await apiClient.get("/accommodation/my-housing")
    return res.data
  },

  selectHousing: async (data: HousingSelectionRequest) => {
    const res = await apiClient.post("/accommodation/select-housing", data)
    return res.data
  },
}
