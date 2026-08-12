export interface AuditEvent {
  event_type: string
  entity_type: string
  entity_id?: string | null
  action: string
  performed_by?: string | null
  details: Record<string, unknown>
  created_at: string
}

export interface AuditSummary {
  total_events: number
  event_types: Record<string, number>
  recent_events: AuditEvent[]
}

export interface AuditList {
  total: number
  page: number
  page_size: number
  events: AuditEvent[]
}
