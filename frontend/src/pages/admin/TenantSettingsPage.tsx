import { useEffect, useState } from "react"
import { AppShell } from "@/components/layout/AppShell"
import { Button } from "@/components/ui/Button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Input } from "@/components/ui/Input"
import { Textarea } from "@/components/ui/Textarea"
import { Select } from "@/components/ui/Select"
import { useAuthStore } from "@/store/authStore"
import { tenantApi } from "@/services/api/tenant"
import { getErrorMessage } from "@/services/api/client"
import type { TenantUpdateRequest } from "@/types/tenant"

const defaultFeatures: Record<string, boolean> = {
  admissions: true,
  finance: true,
  academic: true,
  exam: true,
  accommodation: true,
  library: true,
  hr: true,
  health: true,
  research: true,
  alumni: true,
}

const defaultForm: TenantUpdateRequest = {
  name: "",
  description: "",
  logo_url: "",
  favicon_url: "",
  admin_email: "",
  admin_phone: "",
  country: "Ghana",
  timezone: "Africa/Accra",
  primary_color: "#3b82f6",
  secondary_color: "#8b5cf6",
  accent_color: "#ec4899",
  features: defaultFeatures,
}

export default function TenantSettingsPage() {
  const [tenant, setTenant] = useState<any | null>(null)
  const [form, setForm] = useState<TenantUpdateRequest>(defaultForm)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const storeSelectedTenantId = useAuthStore((s) => s.selectedTenantId)
  const selectedTenantId = storeSelectedTenantId || "single-university"

  useEffect(() => {
    async function loadTenant() {
      setLoading(true)
      setError(null)
      try {
        const data = await tenantApi.getTenant(selectedTenantId)
        setTenant(data)
        setForm({
          name: data.name,
          description: data.description || "",
          logo_url: data.logo_url || "",
          favicon_url: data.favicon_url || "",
          admin_email: data.admin_email,
          admin_phone: data.admin_phone || "",
          country: data.country,
          timezone: data.timezone,
          primary_color: data.primary_color || "#3b82f6",
          secondary_color: data.secondary_color || "#8b5cf6",
          accent_color: data.accent_color || "#ec4899",
          features: data.features || defaultForm.features,
        })
      } catch (err) {
        setError(getErrorMessage(err))
      } finally {
        setLoading(false)
      }
    }

    loadTenant()
  }, [selectedTenantId])

  async function handleSave(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSaving(true)
    setError(null)
    try {
      await tenantApi.updateTenant(selectedTenantId, form)
      setTenant({ ...tenant, ...form })
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setSaving(false)
    }
  }

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink">University Settings</h1>
          <p className="text-cocoa-400">Configure the University of Machelli branding, contacts, and feature access.</p>
        </div>

        <form onSubmit={handleSave} className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <Input label="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
              <Input label="Subdomain" value={tenant?.subdomain || ""} disabled />
            </div>

            <Textarea
              label="Description"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />

            <div className="grid gap-4 sm:grid-cols-2">
              <Input label="Logo URL" value={form.logo_url || ""} onChange={(e) => setForm({ ...form, logo_url: e.target.value })} />
              <Input label="Favicon URL" value={form.favicon_url || ""} onChange={(e) => setForm({ ...form, favicon_url: e.target.value })} />
            </div>

            <div className="grid gap-4 sm:grid-cols-3">
              <Input label="Primary Color" type="color" value={form.primary_color || "#3b82f6"} onChange={(e) => setForm({ ...form, primary_color: e.target.value })} />
              <Input label="Secondary Color" type="color" value={form.secondary_color || "#8b5cf6"} onChange={(e) => setForm({ ...form, secondary_color: e.target.value })} />
              <Input label="Accent Color" type="color" value={form.accent_color || "#ec4899"} onChange={(e) => setForm({ ...form, accent_color: e.target.value })} />
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <Input label="Admin Email" type="email" value={form.admin_email} onChange={(e) => setForm({ ...form, admin_email: e.target.value })} required />
              <Input label="Admin Phone" value={form.admin_phone || ""} onChange={(e) => setForm({ ...form, admin_phone: e.target.value })} />
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <Input label="Country" value={form.country} onChange={(e) => setForm({ ...form, country: e.target.value })} required />
              <Input label="Timezone" value={form.timezone} onChange={(e) => setForm({ ...form, timezone: e.target.value })} required />
            </div>

            <div className="space-y-3">
              <h2 className="text-sm font-medium text-ink">Feature Access</h2>
              <div className="grid gap-2 sm:grid-cols-2">
                {Object.keys(form.features ?? defaultFeatures).map((key) => {
                  const features = form.features ?? defaultFeatures
                  return (
                    <label key={key} className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={features[key] ?? false}
                        onChange={(e) => setForm({
                          ...form,
                          features: {
                            ...features,
                            [key]: e.target.checked,
                          },
                        })}
                      />
                      <span className="text-sm text-ink capitalize">{key.replace(/_/g, " ")}</span>
                    </label>
                  )
                })}
              </div>
            </div>

            {error && <p className="text-sm text-red-600">{error}</p>}
            <Button type="submit" isLoading={saving}>Save university settings</Button>
          </div>

          <div className="space-y-4">
            <Card className="border border-cocoa-100 p-4">
              <CardHeader>
                <CardTitle>Brand Preview</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="rounded-lg border p-4" style={{ backgroundColor: form.primary_color || "#3b82f6" }}>
                    <p className="text-white">Primary color preview</p>
                  </div>
                  <div className="rounded-lg border p-4" style={{ backgroundColor: form.secondary_color || "#8b5cf6" }}>
                    <p className="text-white">Secondary color preview</p>
                  </div>
                  <div className="rounded-lg border p-4" style={{ backgroundColor: form.accent_color || "#ec4899" }}>
                    <p className="text-white">Accent color preview</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border border-cocoa-100 p-4">
              <CardHeader>
                <CardTitle>University Information</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm text-cocoa-600">
                  <div>Name: {tenant?.name}</div>
                  <div>Subdomain: {tenant?.subdomain}</div>
                  <div>Status: {tenant?.is_active ? "Active" : "Inactive"}</div>
                  <div>Trial: {tenant?.is_trial ? "Yes" : "No"}</div>
                </div>
              </CardContent>
            </Card>
          </div>
        </form>
      </div>
    </AppShell>
  )
}
