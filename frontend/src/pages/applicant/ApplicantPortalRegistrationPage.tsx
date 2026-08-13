/**
 * Applicant Portal Registration Page
 * Section 34: APPLICANT PORTAL - Registration
 */

import React, { useState } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import axios from "axios"

export default function ApplicantPortalRegistrationPage() {
  const { schoolCode } = useParams<{ schoolCode: string }>()
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    email: "",
    phone: "",
    password: "",
    password_confirm: "",
    date_of_birth: "",
    gender: "",
    region: "",
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [step, setStep] = useState(1) // Multi-step form

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleNextStep = () => {
    if (step === 1 && (!formData.first_name || !formData.last_name)) {
      setError("Please fill in your name")
      return
    }
    if (step === 2 && (!formData.email || !formData.phone)) {
      setError("Please fill in email and phone")
      return
    }
    setError(null)
    setStep((prev) => prev + 1)
  }

  const handlePrevStep = () => {
    setStep((prev) => prev - 1)
    setError(null)
  }

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    if (formData.password !== formData.password_confirm) {
      setError("Passwords do not match")
      return
    }

    setLoading(true)

    try {
      // Register user
      const registerResponse = await axios.post(`/api/v1/auth/register`, {
        first_name: formData.first_name,
        last_name: formData.last_name,
        email: formData.email,
        password: formData.password,
        phone: formData.phone,
        date_of_birth: formData.date_of_birth,
        gender: formData.gender,
        region: formData.region,
      })

      if (registerResponse.data.user) {
        // Auto-login after registration
        const loginResponse = await axios.post(`/api/v1/auth/login`, {
          email: formData.email,
          password: formData.password,
        })

        if (loginResponse.data.access_token) {
          localStorage.setItem("access_token", loginResponse.data.access_token)
          localStorage.setItem("refresh_token", loginResponse.data.refresh_token)
          localStorage.setItem("current_user", JSON.stringify(loginResponse.data.user))

          // Redirect to dashboard
          navigate(`/apply/${schoolCode}/dashboard`)
        }
      }
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "Registration failed. Please try again."
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4">
      <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Create Application</h1>
        <p className="text-gray-600 mb-6">
          Step {step} of 4: {step === 1 ? "Personal Information" : step === 2 ? "Contact Details" : step === 3 ? "Academic Info" : "Security"}
        </p>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}

        <form onSubmit={step === 4 ? handleRegister : (e) => { e.preventDefault(); handleNextStep(); }} className="space-y-4">
          {/* Step 1: Personal Information */}
          {step === 1 && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  First Name
                </label>
                <Input
                  type="text"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleInputChange}
                  placeholder="John"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Last Name
                </label>
                <Input
                  type="text"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleInputChange}
                  placeholder="Doe"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Date of Birth
                </label>
                <Input
                  type="date"
                  name="date_of_birth"
                  value={formData.date_of_birth}
                  onChange={handleInputChange}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Gender
                </label>
                <select
                  name="gender"
                  value={formData.gender}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                >
                  <option value="">Select gender</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </>
          )}

          {/* Step 2: Contact Details */}
          {step === 2 && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email Address
                </label>
                <Input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  placeholder="you@example.com"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Phone Number
                </label>
                <Input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                  placeholder="+233 5XX XXX XXX"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Region
                </label>
                <Input
                  type="text"
                  name="region"
                  value={formData.region}
                  onChange={handleInputChange}
                  placeholder="e.g., Ashanti Region"
                />
              </div>
            </>
          )}

          {/* Step 3: Academic Info */}
          {step === 3 && (
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-gray-700">
                Academic information will be collected during the application process.
                You'll be prompted to enter your WASSCE results and programme choices.
              </p>
            </div>
          )}

          {/* Step 4: Security */}
          {step === 4 && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Create Password
                </label>
                <Input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  placeholder="••••••••"
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  At least 8 characters, including uppercase, lowercase, and numbers
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Confirm Password
                </label>
                <Input
                  type="password"
                  name="password_confirm"
                  value={formData.password_confirm}
                  onChange={handleInputChange}
                  placeholder="••••••••"
                  required
                />
              </div>

              <div className="bg-blue-50 p-4 rounded-lg text-sm">
                <label className="flex items-start">
                  <input type="checkbox" className="mt-1 mr-2" required />
                  <span className="text-gray-700">
                    I agree to the <a href="#" className="text-blue-600 hover:underline">terms of service</a> and <a href="#" className="text-blue-600 hover:underline">privacy policy</a>
                  </span>
                </label>
              </div>
            </>
          )}

          <div className="flex gap-3 pt-4">
            {step > 1 && (
              <Button
                type="button"
                variant="outline"
                onClick={handlePrevStep}
                className="flex-1"
              >
                Back
              </Button>
            )}
            <Button
              type="submit"
              disabled={loading}
              className="flex-1 bg-blue-600 hover:bg-blue-700"
            >
              {loading ? "Processing..." : step === 4 ? "Create Account" : "Next"}
            </Button>
          </div>
        </form>

        <div className="mt-6 pt-6 border-t border-gray-200 text-center">
          <p className="text-gray-600 text-sm">
            Already have an account?{" "}
            <a
              href={`/apply/${schoolCode}/login`}
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              Sign in
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}
