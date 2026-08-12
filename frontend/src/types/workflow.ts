export interface ApprovalTaskItem {
  id: string
  step_order: number
  status: string
}

export interface ApprovalActionRequest {
  task_id: string
  approved: boolean
  comments?: string
}
