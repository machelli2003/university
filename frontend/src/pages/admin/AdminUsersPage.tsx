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
  const user = useAuthStore((s) => s.user)

  async function load() {
    setLoading(true)
    try {
      const res = await adminApi.listUsers(user?.tenant_id ?? undefined, includeInactive)
      setUsers(res.data)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [user?.tenant_id, includeInactive])

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
          <p className="text-cocoa-400 mb-6">Create, edit, deactivate, and recover university accounts.</p>
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
              <h2 className="text-lg font-medium text-ink">University users</h2>
              <div className="flex items-center gap-2">
                <label className="flex items-center gap-2 text-sm text-cocoa-600">
                  <input
                    type="checkbox"
                    checked={includeInactive}
                    onChange={(e) => setIncludeInactive(e.target.checked)}
                  />
                  Show inactive
                </label>
              </div>
            </div>

            {loading ? (
              <p>Loading...</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm border-collapse">
                  <thead>
                    <tr className="border-b border-cocoa-100 text-xs font-semibold text-cocoa-500 uppercase tracking-wider">
                      <th className="py-3 px-4">Email</th>
                      <th className="py-3 px-4">Name</th>
                      <th className="py-3 px-4">Role</th>
                      <th className="py-3 px-4">Status</th>
                      <th className="py-3 px-4">Locked</th>
                      <th className="py-3 px-4">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-cocoa-100">
                    {users.map((u) => (
                      <tr key={u.id} className={u.is_active ? "hover:bg-cocoa-50/50" : "bg-red-50/50 hover:bg-red-50"}>
                        <td className="py-3 px-4 font-medium text-ink">{u.email}</td>
                        <td className="py-3 px-4 text-cocoa-700">{u.first_name} {u.last_name}</td>
                        <td className="py-3 px-4 text-cocoa-600 font-mono text-xs">{u.role}</td>
                        <td className="py-3 px-4">
                          {u.is_active ? (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              Active
                            </span>
                          ) : (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                              Inactive
                            </span>
                          )}
                        </td>
                        <td className="py-3 px-4">
                          {u.locked_until ? (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800">
                              Locked ({new Date(u.locked_until).toLocaleTimeString()})
                            </span>
                          ) : (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                              No
                            </span>
                          )}
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-2">
                            <button
                              type="button"
                              className="px-2.5 py-1 text-xs font-medium rounded border border-cocoa-200 hover:bg-cocoa-50 text-cocoa-700"
                              onClick={() => setEditingUser(u)}
                            >
                              Edit
                            </button>
                            <button
                              type="button"
                              className="px-2.5 py-1 text-xs font-medium rounded border border-cocoa-200 hover:bg-cocoa-50 text-cocoa-700"
                              onClick={() => handleToggleActive(u)}
                            >
                              {u.is_active ? "Deactivate" : "Activate"}
                            </button>
                            <button
                              type="button"
                              className="px-2.5 py-1 text-xs font-medium rounded border border-cocoa-200 hover:bg-cocoa-50 text-cocoa-700 disabled:opacity-40 disabled:cursor-not-allowed"
                              onClick={() => handleUnlock(u)}
                              disabled={!u.locked_until && u.login_attempts === 0}
                            >
                              Unlock
                            </button>
                          </div>
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
