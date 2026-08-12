import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { communicationApi } from "@/services/api/communication"
import type { SendNotificationRequest, CreateCampaignRequest } from "@/types/communication"

export function useMyNotifications() {
  return useQuery({
    queryKey: ["notifications", "my"],
    queryFn: () => communicationApi.getMyNotifications(),
  })
}

export function useMarkAsRead() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (notificationId: string) => communicationApi.markAsRead(notificationId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notifications", "my"] }),
  })
}

export function useSendNotification() {
  return useMutation({
    mutationFn: (data: SendNotificationRequest) => communicationApi.sendNotification(data),
  })
}

export function useCampaigns() {
  return useQuery({
    queryKey: ["campaigns"],
    queryFn: () => communicationApi.listCampaigns(),
  })
}

export function useCreateCampaign() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: CreateCampaignRequest) => communicationApi.createCampaign(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["campaigns"] }),
  })
}
