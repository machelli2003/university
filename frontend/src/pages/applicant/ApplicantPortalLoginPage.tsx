/**
 * Applicant Portal Login Page
 * Section 34: APPLICANT PORTAL - Login
 */

import React, { useState, useEffect } from "react"
import { useParams, useNavigate, useSearchParams } from "react-router-dom"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import axios from "axios"

export default function ApplicantPortalLoginPage() {
  const { schoolCode } = useParams<{ schoolCode: string }>()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [resetMode, setResetMode] = useState(false)
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")

  useEffect(() => {
    const tempPassword = searchParams.get("tempPassword")
    if (tempPassword) {
      setPassword(tempPassword)
    }
  }, [searchParams])

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      const response = await axios.post(
        `/api/v1/auth/login`,
        { email, password },
        { withCredentials: true }
      )

      if (response.data.access_token) {
        localStorage.setItem("access_token", response.data.access_token)
        localStorage.setItem("refresh_token", response.data.refresh_token)
        localStorage.setItem("current_user", JSON.stringify(response.data.user))

        navigate(`/apply/${schoolCode}/payment`)
      }
    } catch (err: any) {
      const resetRequired = err.response?.status === 403 || err.response?.headers?.["x-password-reset-required"] === "true"
      if (resetRequired) {
        setResetMode(true)
        setError("Your account requires a password reset before you can continue.")
      } else {
        setError(
          err.response?.data?.detail || "Login failed. Please check your credentials and try again."
        )
      }
    } finally {
      setLoading(false)
    }
  }

  const handlePasswordReset = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    if (newPassword.length < 8) {
      setError("New password must be at least 8 characters long")
      return
    }

    if (newPassword !== confirmPassword) {
      setError("New password and confirmation do not match")
      return
    }

    try {
      await axios.post("/api/v1/auth/reset-password", {
        email,
        current_password: password,
        new_password: newPassword,
        confirm_password: confirmPassword,
      })

      setResetMode(false)
      setError(null)
      setNewPassword("")
      setConfirmPassword("")
      const response = await axios.post(`/api/v1/auth/login`, { email, password: newPassword }, { withCredentials: true })
      localStorage.setItem("access_token", response.data.access_token)
      localStorage.setItem("refresh_token", response.data.refresh_token)
      localStorage.setItem("current_user", JSON.stringify(response.data.user))
      navigate(`/apply/${schoolCode}/payment`)
    } catch (err: any) {
      setError(err.response?.data?.detail || "Password reset failed. Please try again.")
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4">
      <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Sign In</h1>
        <p className="text-gray-600 mb-6">Log in to your applicant account for {schoolCode}</p>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}

        {resetMode ? (
          <form onSubmit={handlePasswordReset} className="space-y-4">
            <div>
              <label htmlFor="newPassword" className="block text-sm font-medium text-gray-700 mb-1">
                New Password
              </label>
              <Input
                id="newPassword"
                type="password"
                placeholder="Enter your new password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
                className="w-full"
              />
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
                Confirm New Password
              </label>
              <Input
                id="confirmPassword"
                type="password"
                placeholder="Confirm your new password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                className="w-full"
              />
            </div>

            <Button type="submit" className="w-full py-2 bg-blue-600 hover:bg-blue-700">
              Reset password and continue
            </Button>
          </form>
        ) : (
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                Email Address
              </label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full"
              />
            </div>

            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center">
                <input type="checkbox" className="rounded border-gray-300 mr-2" />
                <span className="text-gray-600">Remember me</span>
              </label>
              <a href="#" className="text-blue-600 hover:text-blue-700 font-medium">
                Forgot password?
              </a>
            </div>

            <Button
              type="submit"
              disabled={loading}
              className="w-full py-2 bg-blue-600 hover:bg-blue-700"
            >
              {loading ? "Signing in..." : "Sign In"}
            </Button>
          </form>
        )}

        <div className="mt-6 pt-6 border-t border-gray-200 text-center">
          <p className="text-gray-600 text-sm">
            Don't have an account?{" "}
            <a
              href={`/apply/${schoolCode}/register`}
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              Create new application
            </a>
          </p>
        </div>

        <div className="mt-6 flex items-center justify-center">
          <Button
            onClick={() => navigate(`/apply/${schoolCode}`)}
            variant="ghost"
            className="text-blue-600 hover:text-blue-700"
          >
            ← Back to portal
          </Button>
        </div>
      </div>
    </div>
  )
}
