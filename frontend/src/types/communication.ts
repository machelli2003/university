export interface NotificationItem {
  id: string
  title: string
  message: string
  is_read: boolean
}

export interface SendNotificationRequest {
  recipient_id: string
  title: string
  message: string
  notification_type?: string
}

export interface CreateCampaignRequest {
  name: string
  message: string
  target_role?: string
}

export interface CampaignItem {
  id: string
  name: string
  message: string
}
