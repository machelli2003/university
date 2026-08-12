import type { FormEvent } from "react"
import { useEffect, useState } from "react"
import { AppShell } from "@/components/layout/AppShell"
import { Button } from "@/components/ui/Button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Input } from "@/components/ui/Input"
import { Select } from "@/components/ui/Select"
import { Textarea } from "@/components/ui/Textarea"
import { useTenants, useCreateTenant, useActivateTenant, useDeactivateTenant } from "@/hooks/useTenant"
import { adminApi } from "@/services/api/admin"
import { getErrorMessage } from "@/services/api/client"
import { useAuthStore } from "@/store/authStore"
import type { Tenant, TenantCreateRequest } from "@/types/tenant"

const defaultForm: TenantCreateRequest = {
  name: "",
  subdomain: "",
  description: "",
  admin_email: "",
  admin_phone: "",
  country: "Ghana",
  timezone: "Africa/Accra",
  subscription_tier: "starter",
}

export default function SuperAdminPage() {
  const [form, setForm] = useState<TenantCreateRequest>(defaultForm)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const tenantsQuery = useTenants(true)
  const createTenantMutation = useCreateTenant()
  const activateTenantMutation = useActivateTenant()
  const deactivateTenantMutation = useDeactivateTenant()
  const selectedTenantId = useAuthStore((s) => s.selectedTenantId)
  const setSelectedTenantId = useAuthStore((s) => s.setSelectedTenantId)
  const [tenantUsers, setTenantUsers] = useState<any[]>([])
  const [tenantUserLoading, setTenantUserLoading] = useState(false)
  const [tenantUserError, setTenantUserError] = useState<string | null>(null)

  const handleCreateTenant = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError(null)
    setSuccess(null)

    try {
      await createTenantMutation.mutateAsync(form)
      setSuccess("Tenant created successfully.")
      setForm(defaultForm)
    } catch (err) {
      setError(getErrorMessage(err))
    }
  }

  const loadTenantUsers = async (tenantId: string | null) => {
    setTenantUserLoading(true)
    setTenantUserError(null)
    try {
      const res = await adminApi.listUsers(tenantId ?? undefined)
      setTenantUsers(res.data)
    } catch (err) {
      setTenantUserError(getErrorMessage(err))
    } finally {
      setTenantUserLoading(false)
    }
  }

  useEffect(() => {
    if (tenantsQuery.data && tenantsQuery.data.length > 0 && !selectedTenantId) {
      setSelectedTenantId(tenantsQuery.data[0].id)
    }
  }, [tenantsQuery.data, selectedTenantId, setSelectedTenantId])

  useEffect(() => {
    if (selectedTenantId) {
      loadTenantUsers(selectedTenantId)
    }
  }, [selectedTenantId])

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink mb-1">Super Admin Console</h1>
          <p className="text-cocoa-400 mb-6">Manage platform-wide configuration, tenant settings, and system-wide user access.</p>
        </div>

        <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <Card>
            <CardHeader>
              <CardTitle>Tenant Management</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-cocoa-500 mb-4">Create tenants and review active tenant settings.</p>

              <form className="space-y-4" onSubmit={handleCreateTenant}>
                <Input
                  label="Tenant Name"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  required
                />
                <Input
                  label="Subdomain"
                  value={form.subdomain}
                  onChange={(e) => setForm({ ...form, subdomain: e.target.value })}
                  required
                />
                <Input
                  label="Admin Email"
                  type="email"
                  value={form.admin_email}
                  onChange={(e) => setForm({ ...form, admin_email: e.target.value })}
                  required
                />
                <Input
                  label="Admin Phone"
                  value={form.admin_phone}
                  onChange={(e) => setForm({ ...form, admin_phone: e.target.value })}
                />
                <Input
                  label="Country"
                  value={form.country}
                  onChange={(e) => setForm({ ...form, country: e.target.value })}
                  required
                />
                <Input
                  label="Timezone"
                  value={form.timezone}
                  onChange={(e) => setForm({ ...form, timezone: e.target.value })}
                  required
                />
                <Select
                  label="Subscription Tier"
                  value={form.subscription_tier}
                  onChange={(e) => setForm({ ...form, subscription_tier: e.target.value })}
                  required
                >
                  <option value="starter">Starter</option>
                  <option value="professional">Professional</option>
                  <option value="enterprise">Enterprise</option>
                </Select>
                <Textarea
                  label="Description"
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                />

                {error && <p className="text-sm text-red-600">{error}</p>}
                {success && <p className="text-sm text-green-600">{success}</p>}

                <Button type="submit" isLoading={createTenantMutation.isPending}>Create Tenant</Button>
              </form>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>System Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-cocoa-500">Only super admins can manage tenants, audit infrastructure, and global settings.</p>
              <div className="mt-4 space-y-2">
                <p className="text-sm text-cocoa-700">Total tenants: {tenantsQuery.data?.length ?? "—"}</p>
                <p className="text-sm text-cocoa-700">Tenant loading: {tenantsQuery.isLoading ? "Loading..." : "Ready"}</p>
                {tenantsQuery.isError && <p className="text-sm text-red-600">{getErrorMessage(tenantsQuery.error)}</p>}
              </div>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Active Tenants</CardTitle>
          </CardHeader>
          <CardContent>
            {tenantsQuery.isLoading && <p>Loading tenants...</p>}
            {tenantsQuery.data && tenantsQuery.data.length === 0 && (
              <p className="text-sm text-cocoa-400">No active tenants available.</p>
            )}
            {tenantsQuery.data && tenantsQuery.data.length > 0 && (
              <div className="space-y-3">
                {tenantsQuery.data.map((tenant) => (
                  <div key={tenant.id} className="rounded-lg border border-cocoa-100 p-4">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <p className="font-semibold text-ink">{tenant.name}</p>
                        <p className="text-sm text-cocoa-500">{tenant.subdomain}</p>
                        <p className="text-sm text-cocoa-500">{tenant.country} · {tenant.timezone}</p>
                        <p className="text-sm text-cocoa-500 mt-1">Status: {tenant.is_active ? "Active" : "Inactive"}</p>
                      </div>
                      <div className="flex flex-col gap-2">
                        {tenant.is_active ? (
                          <Button
                            variant="outline"
                            size="sm"
                            type="button"
                            isLoading={deactivateTenantMutation.isPending}
                            onClick={() => deactivateTenantMutation.mutate(tenant.id)}
                          >
                            Deactivate
                          </Button>
                        ) : (
                          <Button
                            variant="primary"
                            size="sm"
                            type="button"
                            isLoading={activateTenantMutation.isPending}
                            onClick={() => activateTenantMutation.mutate(tenant.id)}
                          >
                            Activate
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Tenant User Oversight</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <Select
                label="Filter by tenant"
                value={selectedTenantId ?? ""}
                onChange={(e) => setSelectedTenantId(e.target.value || null)}
              >
                <option value="">All tenants</option>
                {tenantsQuery.data?.map((tenant) => (
                  <option key={tenant.id} value={tenant.id}>{tenant.name}</option>
                ))}
              </Select>

              {tenantUserLoading ? (
                <p>Loading users...</p>
              ) : tenantUserError ? (
                <p className="text-sm text-red-600">{tenantUserError}</p>
              ) : (
                <div className="space-y-3">
                  {tenantUsers.length === 0 ? (
                    <p className="text-sm text-cocoa-400">No users found for this tenant.</p>
                  ) : (
                    <div className="space-y-2">
                      {tenantUsers.map((user) => (
                        <div key={user.id} className="rounded-lg border border-cocoa-100 p-3">
                          <p className="font-semibold text-ink">{user.first_name} {user.last_name}</p>
                          <p className="text-sm text-cocoa-500">{user.email}</p>
                          <p className="text-sm text-cocoa-500">Role: {user.role}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  )
}
