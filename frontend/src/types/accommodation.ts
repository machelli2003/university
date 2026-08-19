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

export interface HousingSelectionRequest {
  housing_type: "school_hostel" | "outside_hostel" | "private_renting"
  hall_id?: string
  room_id?: string
  outside_hostel_name?: string
  outside_hostel_address?: string
  outside_hostel_contact?: string
  private_address?: string
  private_city?: string
  private_contact?: string
}

export interface StudentHousingStatusResponse {
  student_id: string
  school_fee_paid: boolean
  hostel_fee_paid: boolean
  housing_status: "unassigned" | "school_hostel" | "outside_hostel" | "private_renting"
  hall_id?: string
  hall_name?: string
  room_id?: string
  room_number?: string
  outside_hostel_name?: string
  outside_hostel_address?: string
  outside_hostel_contact?: string
  private_address?: string
  private_city?: string
  private_contact?: string
}

