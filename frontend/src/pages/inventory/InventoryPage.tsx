import { useState } from "react"
import { useForm } from "react-hook-form"
import { AppShell } from "@/components/layout/AppShell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Badge } from "@/components/ui/Badge"
import { ErrorAlert, SuccessAlert, Spinner } from "@/components/ui/Feedback"
import { useCreateAsset, useAssetsByType, useCreateInventoryItem, useLowStock } from "@/hooks/useInventory"
import { getErrorMessage } from "@/services/api/client"
import { formatCurrency } from "@/lib/utils"
import type { CreateAssetRequest, CreateInventoryItemRequest } from "@/types/inventory"

export default function InventoryPage() {
  const [assetType, setAssetType] = useState("equipment")
  const { data: assets, isLoading: assetsLoading } = useAssetsByType(assetType)
  const assetMutation = useCreateAsset()
  const itemMutation = useCreateInventoryItem()
  const { data: lowStock } = useLowStock()

  const assetForm = useForm<CreateAssetRequest>({
    defaultValues: { asset_type: "equipment", name: "", purchase_date: "", purchase_price: 0, location: "" },
  })
  const itemForm = useForm<CreateInventoryItemRequest>({
    defaultValues: { item_name: "", quantity: 0, unit: "pcs", reorder_level: 10 },
  })

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-semibold text-ink mb-1">Inventory</h1>
      <p className="text-cocoa-400 mb-6">Track fixed assets and consumable stock.</p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <Card>
          <CardHeader><CardTitle>Register Asset</CardTitle></CardHeader>
          <CardContent>
            {assetMutation.isError && <ErrorAlert message={getErrorMessage(assetMutation.error)} />}
            {assetMutation.isSuccess && <SuccessAlert message="Asset registered." />}
            <form
              onSubmit={assetForm.handleSubmit((data) =>
                assetMutation.mutate(
                  { ...data, purchase_price: Number(data.purchase_price) },
                  { onSuccess: () => assetForm.reset() }
                )
              )}
              className="space-y-3"
            >
              <Input label="Asset Type" {...assetForm.register("asset_type", { required: true })} />
              <Input label="Name" {...assetForm.register("name", { required: true })} />
              <Input label="Purchase Date" type="date" {...assetForm.register("purchase_date", { required: true })} />
              <Input label="Purchase Price (GHS)" type="number" {...assetForm.register("purchase_price", { required: true })} />
              <Input label="Location" {...assetForm.register("location")} />
              <Button type="submit" isLoading={assetMutation.isPending}>Register Asset</Button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Add Stock Item</CardTitle></CardHeader>
          <CardContent>
            {itemMutation.isError && <ErrorAlert message={getErrorMessage(itemMutation.error)} />}
            {itemMutation.isSuccess && <SuccessAlert message="Stock item added." />}
            <form
              onSubmit={itemForm.handleSubmit((data) =>
                itemMutation.mutate(
                  { ...data, quantity: Number(data.quantity), reorder_level: Number(data.reorder_level) },
                  { onSuccess: () => itemForm.reset() }
                )
              )}
              className="space-y-3"
            >
              <Input label="Item Name" {...itemForm.register("item_name", { required: true })} />
              <div className="grid grid-cols-2 gap-3">
                <Input label="Quantity" type="number" {...itemForm.register("quantity", { required: true })} />
                <Input label="Unit" {...itemForm.register("unit", { required: true })} />
              </div>
              <Input label="Reorder Level" type="number" {...itemForm.register("reorder_level", { required: true })} />
              <Button type="submit" isLoading={itemMutation.isPending}>Add Item</Button>
            </form>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Low Stock Alerts</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-2">
            {lowStock?.map((item) => (
              <div key={item.id} className="flex items-center justify-between border border-cocoa-100 rounded-md px-4 py-2">
                <span className="text-sm font-medium">{item.item_name}</span>
                <Badge variant="danger">{item.quantity} left</Badge>
              </div>
            ))}
            {lowStock && lowStock.length === 0 && (
              <p className="text-sm text-cocoa-400">No items below reorder level.</p>
            )}
          </div>
        </CardContent>
      </Card>
    </AppShell>
  )
}
