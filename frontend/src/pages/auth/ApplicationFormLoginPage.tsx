/**
 * Application Form Login Page
 * Ghana University Model - PIN & Serial Number Login
 * 
 * Applicants login using PIN and Serial number received after
 * purchasing the application form.
 */

import React, { useState } from "react"
import { useNavigate } from "react-router-dom"
import { Button } from "@/components/ui/Button"
import axios from "axios"
import { AlertCircle, Eye, EyeOff, Info } from "lucide-react"

interface LoginFormData {
  pin: string
  serialNumber: string
  email: string
}

export default function ApplicationFormLoginPage() {
  const navigate = useNavigate()
  
  const [formData, setFormData] = useState<LoginFormData>({
    pin: "",
    serialNumber: "",
    email: "",
  })
  
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showPin, setShowPin] = useState(false)
  const [showSerial, setShowSerial] = useState(false)
  const [loginAttempts, setLoginAttempts] = useState(0)

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value.toUpperCase(), // Serial is uppercase
    }))
    setError(null)
  }

  const isFormValid = () => {
    return (
      formData.pin.length === 6 &&
      formData.serialNumber.length === 8 &&
      formData.email.includes("@")
    )
  }

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!isFormValid()) {
      setError("Please enter valid PIN (6 digits) and Serial (8 characters)")
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await axios.post(
        "/api/v1/auth/login/application-form",
        {
          pin: formData.pin,
          serial_number: formData.serialNumber,
          email: formData.email,
        }
      )

      if (response.data.access_token) {
        // Store tokens
        localStorage.setItem("access_token", response.data.access_token)
        localStorage.setItem("refresh_token", response.data.refresh_token)
        localStorage.setItem("current_user", JSON.stringify(response.data.user))
        
        // Redirect to applicant dashboard
        navigate("/applicant/dashboard")
      }
      
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || "Login failed"
      setError(errorMessage)
      setLoginAttempts(prev => prev + 1)
      
      // Blur form after 3 failed attempts
      if (loginAttempts >= 2) {
        setError("Too many login attempts. Please try again later or purchase a new form.")
      }
    } finally {
      setLoading(false)
    }
  }

  const handlePurchaseForm = () => {
    navigate("/application-form/purchase")
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 flex items-center justify-center">
      <div className="w-full max-w-md">
        {/* Card */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-indigo-600 to-blue-600 px-8 py-8 text-center">
            <h1 className="text-3xl font-bold text-white mb-2">
              Application Portal
            </h1>
            <p className="text-indigo-100">
              Login with your PIN and Serial Number
            </p>
          </div>

          {/* Content */}
          <div className="px-8 py-8">
            {/* Info Box */}
            <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg flex gap-3">
              <Info className="text-blue-600 flex-shrink-0 mt-0.5" size={20} />
              <div>
                <p className="text-sm text-blue-900">
                  <strong>First time here?</strong> You must first purchase an application form to get your PIN and Serial Number.
                </p>
              </div>
            </div>

            {/* Error Alert */}
            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex gap-3">
                <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={20} />
                <p className="text-red-800 text-sm">{error}</p>
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleLogin} className="space-y-5">
              {/* Email */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  placeholder="your.email@example.com"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition"
                  disabled={loading}
                  required
                />
              </div>

              {/* PIN */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  PIN (6 digits)
                </label>
                <div className="flex gap-2">
                  <input
                    type={showPin ? "text" : "password"}
                    name="pin"
                    value={formData.pin}
                    onChange={handleInputChange}
                    placeholder="••••••"
                    maxLength={6}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition font-mono text-lg tracking-widest"
                    disabled={loading}
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPin(!showPin)}
                    className="px-3 py-2 hover:bg-gray-100 rounded-lg border border-gray-300 transition"
                    disabled={loading}
                  >
                    {showPin ? <EyeOff size={20} /> : <Eye size={20} />}
                  </button>
                </div>
              </div>

              {/* Serial Number */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Serial Number (8 characters)
                </label>
                <div className="flex gap-2">
                  <input
                    type={showSerial ? "text" : "password"}
                    name="serialNumber"
                    value={formData.serialNumber}
                    onChange={handleInputChange}
                    placeholder="••••••••"
                    maxLength={8}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition font-mono text-lg tracking-widest"
                    disabled={loading}
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowSerial(!showSerial)}
                    className="px-3 py-2 hover:bg-gray-100 rounded-lg border border-gray-300 transition"
                    disabled={loading}
                  >
                    {showSerial ? <EyeOff size={20} /> : <Eye size={20} />}
                  </button>
                </div>
              </div>

              {/* Login Button */}
              <Button
                type="submit"
                disabled={!isFormValid() || loading || loginAttempts > 2}
                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-3 rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed transition mt-6"
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Logging in...
                  </span>
                ) : (
                  "Login to Application Portal"
                )}
              </Button>
            </form>

            {/* Divider */}
            <div className="relative mt-8 mb-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">Don't have PIN and Serial?</span>
              </div>
            </div>

            {/* Purchase Form Button */}
            <Button
              type="button"
              onClick={handlePurchaseForm}
              className="w-full bg-white border-2 border-indigo-600 text-indigo-600 hover:bg-indigo-50 py-3 rounded-lg font-medium transition"
            >
              Purchase Application Form
            </Button>

            {/* Help */}
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <p className="text-xs text-gray-600">
                <strong>Need help?</strong> Contact the admissions office at admissions@university.edu or call +233 XX XXX XXXX
              </p>
            </div>
          </div>
        </div>

        {/* Footer Links */}
        <div className="text-center mt-6">
          <Button
            onClick={() => navigate("/")}
            className="text-white hover:text-gray-200 text-sm font-medium"
          >
            Back to Home
          </Button>
        </div>
      </div>
    </div>
  )
}
