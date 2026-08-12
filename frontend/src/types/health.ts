export interface HealthRecord {
  id: string
  blood_group: string | null
  allergies: string | null
  medical_conditions: string | null
}

export interface CreateHealthRecordRequest {
  student_id: string
  blood_group?: string
  allergies?: string
  medical_conditions?: string
  emergency_contact: string
  emergency_phone: string
}

export interface BookAppointmentRequest {
  student_id: string
  appointment_date: string
  reason: string
}

export interface CounselingRequest {
  topic?: string
  is_anonymous: boolean
}
