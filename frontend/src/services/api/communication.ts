import { apiClient } from "./client"
import type { NotificationItem, SendNotificationRequest, CreateCampaignRequest, CampaignItem } from "@/types/communication"

export const communicationApi = {
  getMyNotifications: async (): Promise<NotificationItem[]> => {
    const res = await apiClient.get("/communication/notifications/my")
    return res.data
  },

  markAsRead: async (notificationId: string) => {
    const res = await apiClient.post(`/communication/notifications/${notificationId}/read`)
    return res.data
  },

  sendNotification: async (data: SendNotificationRequest) => {
    const res = await apiClient.post("/communication/notifications/send", data)
    return res.data
  },

  createCampaign: async (data: CreateCampaignRequest) => {
    const res = await apiClient.post("/communication/campaigns", data)
    return res.data
  },

  listCampaigns: async (): Promise<CampaignItem[]> => {
    const res = await apiClient.get("/communication/campaigns")
    return res.data
  },
}
