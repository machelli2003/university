import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { inventoryApi } from "@/services/api/inventory"
import type { CreateAssetRequest, CreateInventoryItemRequest } from "@/types/inventory"

export function useCreateAsset() {
  return useMutation({
    mutationFn: (data: CreateAssetRequest) => inventoryApi.createAsset(data),
  })
}

export function useAssetsByType(assetType: string) {
  return useQuery({
    queryKey: ["assets", assetType],
    queryFn: () => inventoryApi.listAssetsByType(assetType),
    enabled: !!assetType,
  })
}

export function useCreateInventoryItem() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: CreateInventoryItemRequest) => inventoryApi.createItem(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["low-stock"] }),
  })
}

export function useLowStock() {
  return useQuery({
    queryKey: ["low-stock"],
    queryFn: () => inventoryApi.getLowStock(),
  })
}
