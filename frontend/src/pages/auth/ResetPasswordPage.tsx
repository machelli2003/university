import { type FormEvent, useState } from "react"
import { useNavigate } from "react-router-dom"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { authApi } from "@/services/api/auth"
import { getErrorMessage } from "@/services/api/client"
import { useAuthStore } from "@/store/authStore"
import { ROUTES } from "@/constants/routes"

export default function ResetPasswordPage() {
  const navigate = useNavigate()
  const logout = useAuthStore((s) => s.logout)
  const pendingUser = (() => {
    try {
      return JSON.parse(sessionStorage.getItem("pendingPasswordResetUser") || "{}")
    } catch {
      return {}
    }
  })()

  const [form, setForm] = useState({
    email: pendingUser?.email || "",
    current_password: "",
    new_password: "",
    confirm_password: "",
  })
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError(null)
    setSuccess(null)

    if (!form.email.trim()) {
      setError("Email is required.")
      return
    }

    if (form.new_password !== form.confirm_password) {
      setError("New password and confirmation do not match.")
      return
    }

    try {
      setIsLoading(true)
      await authApi.changePassword(form)
      logout()
      sessionStorage.removeItem("pendingPasswordResetUser")
      setSuccess("Password updated successfully. Please log in again with your new password.")
      setTimeout(() => navigate(ROUTES.LOGIN), 1200)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-paper p-4">
      <div className="w-full max-w-md rounded-lg border border-cocoa-100 bg-white p-6 shadow-sm">
        <h1 className="font-display text-2xl font-semibold text-ink mb-2">Reset Your Password</h1>
        <p className="text-sm text-cocoa-500 mb-6">This account requires a password change before access is granted.</p>

        <form className="space-y-4" onSubmit={handleSubmit}>
          <Input
            label="Email"
            type="email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            required
          />
          <Input
            label="Current Password"
            type="password"
            value={form.current_password}
            onChange={(e) => setForm({ ...form, current_password: e.target.value })}
            required
          />
          <Input
            label="New Password"
            type="password"
            value={form.new_password}
            onChange={(e) => setForm({ ...form, new_password: e.target.value })}
            required
          />
          <Input
            label="Confirm New Password"
            type="password"
            value={form.confirm_password}
            onChange={(e) => setForm({ ...form, confirm_password: e.target.value })}
            required
          />

          {error && <p className="text-sm text-red-600">{error}</p>}
          {success && <p className="text-sm text-green-600">{success}</p>}

          <Button type="submit" className="w-full" isLoading={isLoading}>
            Update Password
          </Button>
        </form>
      </div>
    </div>
  )
}
