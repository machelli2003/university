/**
 * Password Change Form
 * First-Time Password Change
 * 
 * When applicants login with permanent credentials for the first time,
 * they must change their temporary password to a permanent one.
 * This component handles that requirement.
 */

import React, { useState } from "react"
import { useNavigate, useLocation } from "react-router-dom"
import axios from "axios"
import { AlertCircle, Eye, EyeOff, CheckCircle, Lock } from "lucide-react"

interface PasswordChangeFormData {
  currentPassword: string
  newPassword: string
  confirmPassword: string
}

interface LocationState {
  isTemporaryPassword?: boolean
}

export default function PasswordChangeForm() {
  const navigate = useNavigate()
  const location = useLocation()
  const locationState = location.state as LocationState
  const isTemporaryPassword = locationState?.isTemporaryPassword || false
  
  const [formData, setFormData] = useState<PasswordChangeFormData>({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  })
  
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false,
  })
  const [passwordStrength, setPasswordStrength] = useState<"weak" | "medium" | "strong" | null>(null)

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }))
    setError(null)

    // Check password strength
    if (name === "newPassword") {
      checkPasswordStrength(value)
    }
  }

  const checkPasswordStrength = (password: string) => {
    if (password.length < 8) {
      setPasswordStrength("weak")
    } else if (password.length < 12 || !/[A-Z]/.test(password) || !/[0-9]/.test(password)) {
      setPasswordStrength("medium")
    } else if (/[!@#$%^&*]/.test(password)) {
      setPasswordStrength("strong")
    } else {
      setPasswordStrength("medium")
    }
  }

  const isFormValid = () => {
    return (
      formData.currentPassword.length >= 8 &&
      formData.newPassword.length >= 8 &&
      formData.confirmPassword === formData.newPassword &&
      formData.newPassword !== formData.currentPassword
    )
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!isFormValid()) {
      if (formData.newPassword !== formData.confirmPassword) {
        setError("Passwords do not match")
      } else if (formData.newPassword === formData.currentPassword) {
        setError("New password must be different from current password")
      } else {
        setError("Please fill in all fields correctly")
      }
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await axios.post(
        "/api/v1/auth/change-temporary-password",
        {
          old_password: formData.currentPassword,
          new_password: formData.newPassword,
        },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
        }
      )

      setSuccess(true)
      setFormData({
        currentPassword: "",
        newPassword: "",
        confirmPassword: "",
      })

      // Redirect after success
      setTimeout(() => {
        navigate("/dashboard")
      }, 2000)
      
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || "Failed to change password"
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const getStrengthColor = () => {
    switch (passwordStrength) {
      case "weak":
        return "bg-red-500"
      case "medium":
        return "bg-yellow-500"
      case "strong":
        return "bg-green-500"
      default:
        return "bg-gray-300"
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 flex items-center justify-center">
      <div className="w-full max-w-md">
        {/* Card */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-purple-600 to-blue-600 px-8 py-8 text-center">
            <div className="flex justify-center mb-4">
              <Lock className="text-white" size={32} />
            </div>
            <h1 className="text-2xl font-bold text-white mb-2">
              Change Password
            </h1>
            <p className="text-purple-100">
              Secure your account with a new password
            </p>
          </div>

          {/* Content */}
          <div className="px-8 py-8">
            {/* Info Box */}
            {isTemporaryPassword && (
              <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg flex gap-3">
                <AlertCircle className="text-blue-600 flex-shrink-0 mt-0.5" size={20} />
                <div>
                  <p className="text-sm text-blue-900">
                    <strong>First Login:</strong> You must change your temporary password before accessing the system.
                  </p>
                </div>
              </div>
            )}

            {/* Success Alert */}
            {success && (
              <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex gap-3 animate-pulse">
                <CheckCircle className="text-green-600 flex-shrink-0 mt-0.5" size={20} />
                <div>
                  <p className="text-green-800 text-sm font-medium">
                    Password changed successfully!
                  </p>
                  <p className="text-green-700 text-xs">
                    Redirecting to dashboard...
                  </p>
                </div>
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
            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Current Password */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Current Password
                </label>
                <div className="relative">
                  <input
                    type={showPasswords.current ? "text" : "password"}
                    name="currentPassword"
                    value={formData.currentPassword}
                    onChange={handleInputChange}
                    placeholder="Your temporary password"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition"
                    disabled={loading || success}
                  />
                  <button
                    type="button"
                    onClick={() =>
                      setShowPasswords(prev => ({
                        ...prev,
                        current: !prev.current,
                      }))
                    }
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showPasswords.current ? <Eye size={18} /> : <EyeOff size={18} />}
                  </button>
                </div>
              </div>

              {/* New Password */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  New Password
                </label>
                <div className="relative">
                  <input
                    type={showPasswords.new ? "text" : "password"}
                    name="newPassword"
                    value={formData.newPassword}
                    onChange={handleInputChange}
                    placeholder="Create a strong password"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition"
                    disabled={loading || success}
                  />
                  <button
                    type="button"
                    onClick={() =>
                      setShowPasswords(prev => ({
                        ...prev,
                        new: !prev.new,
                      }))
                    }
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showPasswords.new ? <Eye size={18} /> : <EyeOff size={18} />}
                  </button>
                </div>

                {/* Password Strength */}
                {formData.newPassword && (
                  <div className="mt-3">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-medium text-gray-600">
                        Strength:
                      </span>
                      <div className="flex-1 h-1.5 bg-gray-300 rounded-full overflow-hidden">
                        <div
                          className={`h-full ${getStrengthColor()} transition-all duration-300`}
                          style={{
                            width:
                              passwordStrength === "weak"
                                ? "33%"
                                : passwordStrength === "medium"
                                ? "66%"
                                : "100%",
                          }}
                        />
                      </div>
                      <span className="text-xs font-medium text-gray-600 capitalize">
                        {passwordStrength}
                      </span>
                    </div>
                  </div>
                )}

                {/* Password Requirements */}
                <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                  <p className="text-xs font-medium text-gray-700 mb-2">
                    Password must contain:
                  </p>
                  <ul className="space-y-1">
                    <li
                      className={`text-xs flex gap-2 ${
                        formData.newPassword.length >= 8
                          ? "text-green-600"
                          : "text-gray-500"
                      }`}
                    >
                      <span>✓</span>
                      <span>At least 8 characters</span>
                    </li>
                    <li
                      className={`text-xs flex gap-2 ${
                        /[A-Z]/.test(formData.newPassword)
                          ? "text-green-600"
                          : "text-gray-500"
                      }`}
                    >
                      <span>✓</span>
                      <span>One uppercase letter (A-Z)</span>
                    </li>
                    <li
                      className={`text-xs flex gap-2 ${
                        /[0-9]/.test(formData.newPassword)
                          ? "text-green-600"
                          : "text-gray-500"
                      }`}
                    >
                      <span>✓</span>
                      <span>One number (0-9)</span>
                    </li>
                  </ul>
                </div>
              </div>

              {/* Confirm Password */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Confirm Password
                </label>
                <div className="relative">
                  <input
                    type={showPasswords.confirm ? "text" : "password"}
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleInputChange}
                    placeholder="Confirm your new password"
                    className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition ${
                      formData.confirmPassword &&
                      formData.confirmPassword === formData.newPassword
                        ? "border-green-300 bg-green-50"
                        : "border-gray-300"
                    }`}
                    disabled={loading || success}
                  />
                  <button
                    type="button"
                    onClick={() =>
                      setShowPasswords(prev => ({
                        ...prev,
                        confirm: !prev.confirm,
                      }))
                    }
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showPasswords.confirm ? <Eye size={18} /> : <EyeOff size={18} />}
                  </button>
                </div>
                {formData.confirmPassword &&
                  formData.confirmPassword === formData.newPassword && (
                    <p className="text-xs text-green-600 mt-1 flex gap-1">
                      <span>✓</span>
                      <span>Passwords match</span>
                    </p>
                  )}
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={!isFormValid() || loading || success}
                className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 disabled:from-gray-400 disabled:to-gray-400 text-white font-semibold py-2 rounded-lg transition duration-200 flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full" />
                    Changing password...
                  </>
                ) : success ? (
                  <>
                    <CheckCircle size={18} />
                    Password changed!
                  </>
                ) : (
                  "Change Password"
                )}
              </button>
            </form>
          </div>
        </div>

        {/* Security Tips */}
        <div className="mt-8 p-6 bg-white rounded-lg shadow">
          <h3 className="font-semibold text-gray-800 mb-3">Security Tips</h3>
          <ul className="space-y-2 text-sm text-gray-600">
            <li className="flex gap-2">
              <span className="text-purple-600 font-bold">•</span>
              <span>Never share your password with anyone</span>
            </li>
            <li className="flex gap-2">
              <span className="text-purple-600 font-bold">•</span>
              <span>Use a password you haven't used before</span>
            </li>
            <li className="flex gap-2">
              <span className="text-purple-600 font-bold">•</span>
              <span>Avoid using easily guessable information</span>
            </li>
            <li className="flex gap-2">
              <span className="text-purple-600 font-bold">•</span>
              <span>Change your password periodically</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  )
}
