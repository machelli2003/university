import React, { useEffect, useState } from "react"
import { AppShell } from "@/components/layout/AppShell"
import { adminApi } from "@/services/api/admin"
import { getErrorMessage } from "@/services/api/client"
import { useAuthStore } from "@/store/authStore"

const roleOptions = [
  "university_admin",
  "super_admin",
  "registrar",
  "head_of_department",
  "dean",
  "finance_officer",
  "auditor",
  "admissions_officer",
  "lecturer",
  "hostel_administrator",
  "librarian",
  "counselor",
  "parent_guardian",
  "student",
]

export default function AdminUsersPage() {
  const [users, setUsers] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [form, setForm] = useState({ email: "", first_name: "", last_name: "", age: "", password: "", role: "university_admin" })
  const [editingUser, setEditingUser] = useState<any | null>(null)
  const [includeInactive, setIncludeInactive] = useState(false)
  const selectedTenantId = useAuthStore((s) => s.selectedTenantId)

  async function load() {
    setLoading(true)
    try {
      const res = await adminApi.listUsers(selectedTenantId ?? undefined, includeInactive)
      setUsers(res.data)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [selectedTenantId, includeInactive])

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    try {
      const createPayload = {
        ...form,
        age: form.age ? Number(form.age) : undefined,
      }
      await adminApi.createUser(createPayload)
      setForm({ email: "", first_name: "", last_name: "", age: "", password: "", role: "university_admin" })
      await load()
    } catch (err) {
      setError(getErrorMessage(err))
    }
  }

  async function handleSaveChanges(e: React.FormEvent) {
    e.preventDefault()
    if (!editingUser) return
    setError(null)
    try {
      const payload = {
        first_name: editingUser.first_name,
        last_name: editingUser.last_name,
        age: editingUser.age,
        role: editingUser.role,
        is_active: editingUser.is_active,
      }
      await adminApi.updateUser(editingUser.id, payload)
      setEditingUser(null)
      await load()
    } catch (err) {
      setError(getErrorMessage(err))
    }
  }

  async function handleToggleActive(user: any) {
    setError(null)
    try {
      await adminApi.updateUser(user.id, { is_active: !user.is_active })
      await load()
    } catch (err) {
      setError(getErrorMessage(err))
    }
  }

  async function handleUnlock(user: any) {
    setError(null)
    try {
      await adminApi.unlockUser(user.id)
      await load()
    } catch (err) {
      setError(getErrorMessage(err))
    }
  }

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink mb-1">User Management</h1>
          <p className="text-cocoa-400 mb-6">Create, edit, deactivate, and recover accounts for your tenant.</p>
        </div>

        <div className="grid gap-6 lg:grid-cols-[1fr_1.5fr]">
          <div className="space-y-4">
            <form onSubmit={handleCreate} className="space-y-3 rounded-lg border border-cocoa-100 p-4">
              <h2 className="text-lg font-medium text-ink">Create new user</h2>
              <input
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                placeholder="Email"
                className="w-full input"
              />
              <input
                value={form.first_name}
                onChange={(e) => setForm({ ...form, first_name: e.target.value })}
                placeholder="First name"
                className="w-full input"
              />
              <input
                value={form.last_name}
                onChange={(e) => setForm({ ...form, last_name: e.target.value })}
                placeholder="Last name"
                className="w-full input"
              />
              <input
                value={form.age}
                onChange={(e) => setForm({ ...form, age: e.target.value })}
                placeholder="Age"
                type="number"
                className="w-full input"
              />
              <input
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                placeholder="Password"
                type="password"
                className="w-full input"
              />
              <select
                value={form.role}
                onChange={(e) => setForm({ ...form, role: e.target.value })}
                className="w-full input"
              >
                {roleOptions.map((role) => (
                  <option key={role} value={role}>{role.replace(/_/g, " ")}</option>
                ))}
              </select>
              <button className="btn btn-primary w-full" type="submit">Create user</button>
            </form>

            {editingUser && (
              <form onSubmit={handleSaveChanges} className="space-y-3 rounded-lg border border-cocoa-100 p-4">
                <h2 className="text-lg font-medium text-ink">Edit user</h2>
                <input
                  value={editingUser.first_name}
                  onChange={(e) => setEditingUser({ ...editingUser, first_name: e.target.value })}
                  placeholder="First name"
                  className="w-full input"
                />
                <input
                  value={editingUser.last_name}
                  onChange={(e) => setEditingUser({ ...editingUser, last_name: e.target.value })}
                  placeholder="Last name"
                  className="w-full input"
                />
                <input
                  value={editingUser.age ?? ""}
                  onChange={(e) => setEditingUser({ ...editingUser, age: e.target.value ? Number(e.target.value) : undefined })}
                  placeholder="Age"
                  type="number"
                  className="w-full input"
                />
                <select
                  value={editingUser.role}
                  onChange={(e) => setEditingUser({ ...editingUser, role: e.target.value })}
                  className="w-full input"
                >
                  {roleOptions.map((role) => (
                    <option key={role} value={role}>{role.replace(/_/g, " ")}</option>
                  ))}
                </select>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={editingUser.is_active}
                    onChange={(e) => setEditingUser({ ...editingUser, is_active: e.target.checked })}
                  />
                  <span className="text-sm text-ink">Active account</span>
                </label>
                <div className="flex gap-2">
                  <button className="btn btn-primary" type="submit">Save changes</button>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => setEditingUser(null)}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            )}
          </div>

          <div className="rounded-lg border border-cocoa-100 p-4">
            <div className="flex items-center justify-between gap-3 mb-4">
              <h2 className="text-lg font-medium text-ink">Tenant users</h2>
              <label className="flex items-center gap-2 text-sm text-cocoa-600">
                <input
                  type="checkbox"
                  checked={includeInactive}
                  onChange={(e) => setIncludeInactive(e.target.checked)}
                />
                Show inactive
              </label>
            </div>

            {loading ? (
              <p>Loading...</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full table-auto">
                  <thead>
                    <tr>
                      <th className="text-left">Email</th>
                      <th className="text-left">Name</th>
                      <th className="text-left">Role</th>
                      <th className="text-left">Status</th>
                      <th className="text-left">Locked</th>
                      <th className="text-left">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((u) => (
                      <tr key={u.id} className={u.is_active ? "" : "bg-red-50"}>
                        <td>{u.email}</td>
                        <td>{u.first_name} {u.last_name}</td>
                        <td>{u.role}</td>
                        <td>{u.is_active ? "Active" : "Inactive"}</td>
                        <td>{u.locked_until ? new Date(u.locked_until).toLocaleString() : "No"}</td>
                        <td className="space-x-2">
                          <button
                            type="button"
                            className="btn btn-outline btn-sm"
                            onClick={() => setEditingUser(u)}
                          >
                            Edit
                          </button>
                          <button
                            type="button"
                            className="btn btn-outline btn-sm"
                            onClick={() => handleToggleActive(u)}
                          >
                            {u.is_active ? "Deactivate" : "Activate"}
                          </button>
                          <button
                            type="button"
                            className="btn btn-outline btn-sm"
                            onClick={() => handleUnlock(u)}
                            disabled={!u.locked_until && u.login_attempts === 0}
                          >
                            Unlock
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            {error && <p className="text-sm text-red-500 mt-3">{error}</p>}
          </div>
        </div>
      </div>
    </AppShell>
  )
}
