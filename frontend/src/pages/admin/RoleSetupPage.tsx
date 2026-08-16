import { useState } from "react"
import { AppShell } from "@/components/layout/AppShell"
import { adminApi } from "@/services/api/admin"
import { getErrorMessage } from "@/services/api/client"
import { Plus, Trash2 } from "lucide-react"

const STAFF_ROLES = [
  { value: "registrar", label: "Registrar", description: "Manages academic records and student progression" },
  { value: "admissions_officer", label: "Admissions Officer", description: "Handles admissions and applications" },
  { value: "head_of_department", label: "Head of Department", description: "Manages department operations" },
  { value: "dean", label: "Dean", description: "Manages faculty operations" },
  { value: "finance_officer", label: "Finance Officer", description: "Handles finance and payments" },
  { value: "hostel_administrator", label: "Hostel Administrator", description: "Manages accommodation" },
  { value: "librarian", label: "Librarian", description: "Manages library resources" },
  { value: "lecturer", label: "Lecturer", description: "Teaches courses and manages grades" },
  { value: "counselor", label: "Counselor", description: "Provides student counseling" },
  { value: "auditor", label: "Auditor", description: "Audits university operations" },
]

interface StaffMember {
  first_name: string
  last_name: string
  email: string
  role: string
  password: string
}

export default function RoleSetupPage() {
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [staff, setStaff] = useState<StaffMember[]>([
    { first_name: "", last_name: "", email: "", role: "registrar", password: "" },
  ])

  function addStaffRow() {
    setStaff([
      ...staff,
      { first_name: "", last_name: "", email: "", role: "registrar", password: "" },
    ])
  }

  function removeStaffRow(index: number) {
    setStaff(staff.filter((_, i) => i !== index))
  }

  function updateStaffRow(index: number, field: keyof StaffMember, value: string) {
    const updated = [...staff]
    updated[index] = { ...updated[index], [field]: value }
    setStaff(updated)
  }

  async function handleCreateStaff(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setMessage(null)
    setLoading(true)

    try {
      const validStaff = staff.filter(
        (s) => s.first_name.trim() && s.last_name.trim() && s.email.trim() && s.password.trim()
      )

      if (validStaff.length === 0) {
        throw new Error("Please fill in at least one staff member with all required fields")
      }

      let createdCount = 0
      for (const s of validStaff) {
        try {
          await adminApi.createUser({
            email: s.email,
            first_name: s.first_name,
            last_name: s.last_name,
            role: s.role,
            password: s.password,
            age: 0,
            permissions: [],
          })
          createdCount++
        } catch (err) {
          console.error(`Failed to create ${s.email}:`, err)
        }
      }

      setMessage(`Successfully created ${createdCount} staff member(s)`)
      setStaff([{ first_name: "", last_name: "", email: "", role: "registrar", password: "" }])
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink mb-1">Staff & Role Setup</h1>
          <p className="text-cocoa-400 mb-6">Create and assign staff members to different roles in your university.</p>
        </div>

        {message && <div className="rounded border border-green-200 bg-green-50 px-4 py-3 text-green-700">{message}</div>}
        {error && <div className="rounded border border-red-200 bg-red-50 px-4 py-3 text-red-700">{error}</div>}

        {/* AVAILABLE ROLES */}
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
          {STAFF_ROLES.map((roleInfo) => (
            <div key={roleInfo.value} className="rounded-lg border border-cocoa-100 p-4 bg-white">
              <h3 className="font-semibold text-ink">{roleInfo.label}</h3>
              <p className="text-sm text-cocoa-600 mt-1">{roleInfo.description}</p>
            </div>
          ))}
        </div>

        {/* STAFF CREATION FORM */}
        <div className="rounded-lg border border-cocoa-100 p-6 bg-white">
          <h2 className="text-lg font-semibold text-ink mb-6">Add Staff Members</h2>

          <form onSubmit={handleCreateStaff} className="space-y-4">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-cocoa-200">
                    <th className="px-3 py-2 text-left font-medium text-cocoa-700">First Name</th>
                    <th className="px-3 py-2 text-left font-medium text-cocoa-700">Last Name</th>
                    <th className="px-3 py-2 text-left font-medium text-cocoa-700">Email</th>
                    <th className="px-3 py-2 text-left font-medium text-cocoa-700">Role</th>
                    <th className="px-3 py-2 text-left font-medium text-cocoa-700">Password</th>
                    <th className="px-3 py-2 text-left font-medium text-cocoa-700">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {staff.map((member, idx) => (
                    <tr key={idx} className="border-b border-cocoa-100">
                      <td className="px-3 py-2">
                        <input
                          className="w-full input text-sm py-1"
                          type="text"
                          placeholder="First name"
                          value={member.first_name}
                          onChange={(e) => updateStaffRow(idx, "first_name", e.target.value)}
                        />
                      </td>
                      <td className="px-3 py-2">
                        <input
                          className="w-full input text-sm py-1"
                          type="text"
                          placeholder="Last name"
                          value={member.last_name}
                          onChange={(e) => updateStaffRow(idx, "last_name", e.target.value)}
                        />
                      </td>
                      <td className="px-3 py-2">
                        <input
                          className="w-full input text-sm py-1"
                          type="email"
                          placeholder="email@school.edu"
                          value={member.email}
                          onChange={(e) => updateStaffRow(idx, "email", e.target.value)}
                        />
                      </td>
                      <td className="px-3 py-2">
                        <select
                          className="w-full input text-sm py-1"
                          value={member.role}
                          onChange={(e) => updateStaffRow(idx, "role", e.target.value)}
                        >
                          {STAFF_ROLES.map((r) => (
                            <option key={r.value} value={r.value}>
                              {r.label}
                            </option>
                          ))}
                        </select>
                      </td>
                      <td className="px-3 py-2">
                        <input
                          className="w-full input text-sm py-1"
                          type="password"
                          placeholder="Temporary password"
                          value={member.password}
                          onChange={(e) => updateStaffRow(idx, "password", e.target.value)}
                        />
                      </td>
                      <td className="px-3 py-2">
                        {staff.length > 1 && (
                          <button
                            type="button"
                            onClick={() => removeStaffRow(idx)}
                            className="text-red-600 hover:text-red-800"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* ADD ROW BUTTON */}
            <button
              type="button"
              onClick={addStaffRow}
              className="btn btn-secondary flex items-center gap-2 w-full justify-center"
            >
              <Plus className="h-4 w-4" /> Add Another Staff Member
            </button>

            {/* SUBMIT BUTTON */}
            <div className="flex gap-3 pt-4">
              <button type="submit" disabled={loading} className="btn btn-primary">
                {loading ? "Creating Staff..." : "Create All Staff Members"}
              </button>
            </div>
          </form>
        </div>

        {/* NOTES */}
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-4">
          <p className="text-sm text-amber-900">
            <strong>Note:</strong> Staff members will receive their temporary passwords. They should log in and change
            their password on first login.
          </p>
        </div>
      </div>
    </AppShell>
  )
}
