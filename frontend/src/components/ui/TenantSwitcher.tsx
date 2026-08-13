import { useMemo, type ChangeEvent } from "react"
import { useAuthStore } from "@/store/authStore"
import type { Tenant } from "@/types/tenant"
import { adminApi } from "@/services/api/admin"
import { getErrorMessage } from "@/services/api/client"
import { useState } from "react"

interface TenantSwitcherProps {
  tenants: Tenant[]
}

export function TenantSwitcher({ tenants }: TenantSwitcherProps) {
  const selectedTenantId = useAuthStore((state) => state.selectedTenantId)
  const setSelectedTenantId = useAuthStore((state) => state.setSelectedTenantId)
  const startImpersonation = useAuthStore((s) => s.startImpersonation)
  const stopImpersonation = useAuthStore((s) => s.stopImpersonation)
  const user = useAuthStore((s) => s.user)
  const [error, setError] = useState<string | null>(null)

  const options = useMemo(
    () => [{ id: "", name: "All tenants" }, ...tenants],
    [tenants]
  )

  const handleChange = (event: ChangeEvent<HTMLSelectElement>) => {
    const newTenant = event.target.value || null

    // If super admin selects a specific tenant, request impersonation token
    if (user?.role === "super_admin" && newTenant) {
      setError(null)
      adminApi.impersonate(newTenant)
        .then((res) => {
          const token = res.data?.access_token
          if (token) {
            startImpersonation(token, null)
            setSelectedTenantId(newTenant)
          } else {
            setError("Unable to impersonate tenant")
          }
        })
        .catch((err: unknown) => setError(getErrorMessage(err)))
    } else if (user?.role === "super_admin" && !newTenant) {
      setError(null)
      adminApi.stopImpersonation()
        .then(() => {
          stopImpersonation()
          setSelectedTenantId(null)
        })
        .catch((err: unknown) => {
          setError(getErrorMessage(err))
        })
    } else {
      setSelectedTenantId(newTenant)
    }
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
      {error && <div className="text-xs text-red-500 mt-1">{error}</div>}
    </div>
  )
}
