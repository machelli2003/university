export interface CreateAssetRequest {
  asset_type: string
  name: string
  description?: string
  purchase_date: string
  purchase_price: number
  location?: string
}

export interface AssetItem {
  id: string
  name: string
  current_value: number
}

export interface CreateInventoryItemRequest {
  item_name: string
  quantity: number
  unit: string
  reorder_level: number
}

export interface InventoryItem {
  id: string
  item_name: string
  quantity: number
}
