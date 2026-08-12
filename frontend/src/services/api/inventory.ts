import { apiClient } from "./client"
import type { CreateAssetRequest, AssetItem, CreateInventoryItemRequest, InventoryItem } from "@/types/inventory"

export const inventoryApi = {
  createAsset: async (data: CreateAssetRequest) => {
    const res = await apiClient.post("/inventory/assets", data)
    return res.data
  },

  listAssetsByType: async (assetType: string): Promise<AssetItem[]> => {
    const res = await apiClient.get(`/inventory/assets/type/${assetType}`)
    return res.data
  },

  createItem: async (data: CreateInventoryItemRequest) => {
    const res = await apiClient.post("/inventory/items", data)
    return res.data
  },

  getLowStock: async (): Promise<InventoryItem[]> => {
    const res = await apiClient.get("/inventory/items/low-stock")
    return res.data
  },
}
