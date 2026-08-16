import { useState } from "react"
import { AppShell } from "@/components/layout/AppShell"
import { Button } from "@/components/ui/Button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Input } from "@/components/ui/Input"
import { adminApi } from "@/services/api/admin"
import { getErrorMessage } from "@/services/api/client"
import { useAuthStore } from "@/store/authStore"

export default function SuperAdminPage() {
  const user = useAuthStore((s) => s.user)
  const [adminForm, setAdminForm] = useState({
    email: "",
    first_name: "",
    last_name: "",
    password: "",
  })
  const [adminCreateError, setAdminCreateError] = useState<string | null>(null)
  const [adminCreateSuccess, setAdminCreateSuccess] = useState<string | null>(null)
  const [adminCreating, setAdminCreating] = useState(false)

  const handleCreateUniversityAdmin = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setAdminCreateError(null)
    setAdminCreateSuccess(null)

    try {
      setAdminCreating(true)
      const password = adminForm.password || "UniversityAdmin@2026"
      const tenantId = user?.tenant_id || "single-university"

      await adminApi.createUser({
        email: adminForm.email,
        first_name: adminForm.first_name,
        last_name: adminForm.last_name,
        password,
        role: "university_admin",
        tenant_id: tenantId,
        must_change_password: true,
      })

      setAdminCreateSuccess(`University admin created for University of Machelli. Default password: ${password}. They must change it on first login.`)
      setAdminForm({ email: "", first_name: "", last_name: "", password: "" })
    } catch (err) {
      setAdminCreateError(getErrorMessage(err))
    } finally {
      setAdminCreating(false)
    }
  }

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink mb-1">University of Machelli</h1>
          <p className="text-cocoa-400 mb-6">Single-university administration. Create the university administrator from here.</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Create University Admin</CardTitle>
          </CardHeader>
          <CardContent>
            <form className="space-y-4" onSubmit={handleCreateUniversityAdmin}>
              <Input
                label="University Admin Email"
                type="email"
                value={adminForm.email}
                onChange={(e) => setAdminForm({ ...adminForm, email: e.target.value })}
                required
              />
              <div className="grid gap-4 sm:grid-cols-2">
                <Input
                  label="First Name"
                  value={adminForm.first_name}
                  onChange={(e) => setAdminForm({ ...adminForm, first_name: e.target.value })}
                  required
                />
                <Input
                  label="Last Name"
                  value={adminForm.last_name}
                  onChange={(e) => setAdminForm({ ...adminForm, last_name: e.target.value })}
                  required
                />
              </div>
              <Input
                label="Default Password"
                type="text"
                value={adminForm.password}
                onChange={(e) => setAdminForm({ ...adminForm, password: e.target.value })}
                placeholder="Leave blank to use UniversityAdmin@2026"
              />
              {adminCreateError && <p className="text-sm text-red-600">{adminCreateError}</p>}
              {adminCreateSuccess && <p className="text-sm text-green-600">{adminCreateSuccess}</p>}
              <Button type="submit" isLoading={adminCreating}>Create University Admin</Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  )
}
