export interface LeaveRequest {
  leave_type: string
  start_date: string
  end_date: string
  reason: string
}

export interface LeaveItem {
  id: string
  staff_id: string
  leave_type: string
  reason: string
}

export interface StaffMember {
  id: string
  first_name: string
  last_name: string
  position: string
}
