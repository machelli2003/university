/**
 * Permanent Credential Login Page
 * Real Credentials Login (After Acceptance)
 * 
 * Applicants who have been OFFERED admission use this page
 * to login with their username and password (which was issued
 * after they were accepted).
 * 
 * On first login, they'll be prompted to change their temporary password.
 */

import React, { useState } from "react"
import { useNavigate, useLocation } from "react-router-dom"
import axios from "axios"
import { AlertCircle, Eye, EyeOff, Info, CheckCircle } from "lucide-react"

interface LoginFormData {
  username: string
  password: string
}

interface LocationState {
  from?: string
  message?: string
}

export default function PermanentCredentialLoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const locationState = location.state as LocationState
  
  const [formData, setFormData] = useState<LoginFormData>({
    username: "",
    password: "",
  })
  
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [showPassword, setShowPassword] = useState(false)

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }))
    setError(null)
  }

  const isFormValid = () => {
    return formData.username.length >= 3 && formData.password.length >= 8
  }

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!isFormValid()) {
      setError("Please enter valid username and password")
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await axios.post(
        "/api/v1/auth/login/permanent-credential",
        {
          username: formData.username,
          password: formData.password,
        }
      )

      if (response.data.access_token) {
        // Store tokens
        localStorage.setItem("access_token", response.data.access_token)
        localStorage.setItem("refresh_token", response.data.refresh_token)
        localStorage.setItem("current_user", JSON.stringify(response.data.user))
        
        // Check if password change is required
        if (response.data.user.must_change_password) {
          // Redirect to password change page
          setSuccess("Login successful! You must change your password now.")
          setTimeout(() => {
            navigate("/change-password", { 
              state: { isTemporaryPassword: true } 
            })
          }, 1500)
        } else {
          // Redirect to dashboard
          setSuccess("Login successful!")
          const redirectPath = locationState?.from || "/dashboard"
          setTimeout(() => {
            navigate(redirectPath)
          }, 1000)
        }
      }
      
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || "Login failed"
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 flex items-center justify-center">
      <div className="w-full max-w-md">
        {/* Card */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-green-600 to-blue-600 px-8 py-8 text-center">
            <h1 className="text-3xl font-bold text-white mb-2">
              Student Portal
            </h1>
            <p className="text-green-100">
              Login with your credentials
            </p>
          </div>

          {/* Content */}
          <div className="px-8 py-8">
            {/* Info Box */}
            <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex gap-3">
              <Info className="text-green-600 flex-shrink-0 mt-0.5" size={20} />
              <div>
                <p className="text-sm text-green-900">
                  <strong>Congratulations!</strong> You've been offered admission. Use the username and password from your admission letter to login.
                </p>
              </div>
            </div>

            {/* Success Alert */}
            {success && (
              <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex gap-3">
                <CheckCircle className="text-green-600 flex-shrink-0 mt-0.5" size={20} />
                <p className="text-green-800 text-sm">{success}</p>
              </div>
            )}

            {/* Error Alert */}
            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex gap-3">
                <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={20} />
                <p className="text-red-800 text-sm">{error}</p>
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleLogin} className="space-y-5">
              {/* Username */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Username
                </label>
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleInputChange}
                  placeholder="your.username"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition"
                  disabled={loading}
                />
                <p className="text-xs text-gray-500 mt-1">
                  This was sent in your admission letter
                </p>
              </div>

              {/* Password */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <label className="block text-sm font-medium text-gray-700">
                    Password
                  </label>
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="text-xs text-green-600 hover:text-green-700 font-medium"
                  >
                    {showPassword ? "Hide" : "Show"}
                  </button>
                </div>
                <div className="relative">
                  <input
                    type={showPassword ? "text" : "password"}
                    name="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    placeholder="Your password"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition pr-10"
                    disabled={loading}
                  />
                  <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400">
                    {showPassword ? <Eye size={18} /> : <EyeOff size={18} />}
                  </div>
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={!isFormValid() || loading}
                className="w-full bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 disabled:from-gray-400 disabled:to-gray-400 text-white font-semibold py-2 rounded-lg transition duration-200 flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full" />
                    Logging in...
                  </>
                ) : (
                  "Login"
                )}
              </button>
            </form>

            {/* Divider */}
            <div className="my-6 relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">or</span>
              </div>
            </div>

            {/* Alternative Login */}
            <p className="text-center text-sm text-gray-600">
              <span className="text-gray-600">Using PIN and Serial number?{" "}</span>
              <button
                onClick={() => navigate("/auth/application-form-login")}
                className="text-green-600 hover:text-green-700 font-medium hover:underline"
              >
                Use Application Form Login
              </button>
            </p>
          </div>
        </div>

        {/* Footer Help */}
        <div className="mt-8 p-6 bg-white rounded-lg shadow">
          <h3 className="font-semibold text-gray-800 mb-3">Having trouble?</h3>
          <ul className="space-y-2 text-sm text-gray-600">
            <li className="flex gap-2">
              <span className="text-green-600 font-bold">•</span>
              <span>Check your admission letter for your username</span>
            </li>
            <li className="flex gap-2">
              <span className="text-green-600 font-bold">•</span>
              <span>Password must be at least 8 characters</span>
            </li>
            <li className="flex gap-2">
              <span className="text-green-600 font-bold">•</span>
              <span>On first login, you must change your temporary password</span>
            </li>
            <li className="flex gap-2">
              <span className="text-green-600 font-bold">•</span>
              <span>Contact admissions if you didn't receive credentials</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  )
}
