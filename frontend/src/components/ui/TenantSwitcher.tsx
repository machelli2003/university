import { useMemo, type ChangeEvent } from "react"
import { useAuthStore } from "@/store/authStore"
import type { Tenant } from "@/types/tenant"

interface TenantSwitcherProps {
  tenants: Tenant[]
}

export function TenantSwitcher({ tenants }: TenantSwitcherProps) {
  const selectedTenantId = useAuthStore((state) => state.selectedTenantId)
  const setSelectedTenantId = useAuthStore((state) => state.setSelectedTenantId)

  const options = useMemo(
    () => [{ id: "", name: "All tenants" }, ...tenants],
    [tenants]
  )

  const handleChange = (event: ChangeEvent<HTMLSelectElement>) => {
    setSelectedTenantId(event.target.value || null)
  }

  return (
    <div className="space-y-1">
      <label htmlFor="tenant-switcher" className="block text-sm font-medium text-cocoa-800">
        Tenant context
      </label>
      <select
        id="tenant-switcher"
        value={selectedTenantId ?? ""}
        onChange={handleChange}
        className="w-full rounded-md border border-cocoa-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-cocoa-400 focus:border-transparent"
      >
        {options.map((tenant) => (
          <option key={tenant.id || "all"} value={tenant.id || ""}>
            {tenant.name}
          </option>
        ))}
      </select>
    </div>
  )
}
