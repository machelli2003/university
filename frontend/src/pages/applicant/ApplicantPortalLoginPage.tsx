/**
 * Applicant Portal Login Page
 * Section 34: APPLICANT PORTAL - Login
 */

import React, { useState } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import axios from "axios"

export default function ApplicantPortalLoginPage() {
  const { schoolCode } = useParams<{ schoolCode: string }>()
  const navigate = useNavigate()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

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

        // Redirect to dashboard
        navigate(`/apply/${schoolCode}/dashboard`)
      }
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "Login failed. Please check your credentials and try again."
      )
    } finally {
      setLoading(false)
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
