export interface Hall {
  id: string
  name: string
  capacity: number
}

export interface Room {
  id: string
  hall_id: string
  room_number: string
  room_type: string
  capacity: number
  occupied: number
  is_active: boolean
}

export interface AllocateRoomRequest {
  student_id: string
  hall_id: string
  room_id: string
}

export interface MaintenanceRequestCreate {
  hall_id: string
  room_id?: string
  issue_description: string
}

export interface MaintenanceRequestItem {
  id: string
  hall_id: string
  room_id?: string
  issue_description: string
  status: string
  assigned_to?: string
  created_date?: string
  resolved_date?: string
}

export interface OccupancyHallBreakdown {
  hall_id: string
  hall_name: string
  room_count: number
  capacity: number
  occupied: number
}

export interface OccupancySummaryResponse {
  total_halls: number
  total_rooms: number
  total_capacity: number
  total_occupied: number
  vacancy_rate: number
  halls: OccupancyHallBreakdown[]
}

export interface RoomOccupantResponse {
  student_id: string
  hall_id: string
  room_id: string
  check_in_date?: string
  check_out_date?: string
  is_active: boolean
}
