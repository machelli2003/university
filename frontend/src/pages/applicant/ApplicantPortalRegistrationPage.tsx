/**
 * Applicant Portal Registration Page
 * Section 34: APPLICANT PORTAL - Registration (FEE-FIRST FLOW)
 * 
 * After registration, applicant is redirected to payment page.
 * Payment must be completed before accessing the application form.
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
      const registerResponse = await axios.post(`/api/v1/apply/${schoolCode}/register`, {
        first_name: formData.first_name,
        last_name: formData.last_name,
        email: formData.email,
        password: formData.password,
        phone: formData.phone,
      })

      if (registerResponse.data.status === "success") {
        const tempPassword = registerResponse.data.temporary_password

        // If temporary password was generated (must_change_password = true)
        if (tempPassword) {
          // Login with temporary password first
          try {
            const loginResponse = await axios.post(`/api/v1/auth/login`, {
              email: formData.email,
              password: tempPassword,
            })

            if (loginResponse.data.access_token) {
              localStorage.setItem("access_token", loginResponse.data.access_token)
              localStorage.setItem("refresh_token", loginResponse.data.refresh_token)
              localStorage.setItem("current_user", JSON.stringify(loginResponse.data.user))
              
              // FEE-FIRST FLOW: Redirect to payment (required gate before form access)
              navigate(`/apply/${schoolCode}/payment`)
            }
          } catch (loginErr: any) {
            setError("Registration successful but login failed. Please try logging in manually.")
          }
          return
        }

        // Otherwise login with provided password
        try {
          const loginResponse = await axios.post(`/api/v1/auth/login`, {
            email: formData.email,
            password: formData.password,
          })

          if (loginResponse.data.access_token) {
            localStorage.setItem("access_token", loginResponse.data.access_token)
            localStorage.setItem("refresh_token", loginResponse.data.refresh_token)
            localStorage.setItem("current_user", JSON.stringify(loginResponse.data.user))
            
            // FEE-FIRST FLOW: Redirect to payment (required gate before form access)
            navigate(`/apply/${schoolCode}/payment`)
          }
        } catch (loginErr: any) {
          setError("Registration successful but login failed. Please try logging in manually.")
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
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Create Your Account</h1>
        <p className="text-gray-600 mb-6">
          Step {step} of 3
        </p>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}

        <form onSubmit={handleRegister} className="space-y-4">
          {/* Step 1: Name */}
          {step === 1 && (
            <>
              <div>
                <label className="block text-gray-700 text-sm font-semibold mb-2">
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
                <label className="block text-gray-700 text-sm font-semibold mb-2">
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
            </>
          )}

          {/* Step 2: Contact */}
          {step === 2 && (
            <>
              <div>
                <label className="block text-gray-700 text-sm font-semibold mb-2">
                  Email
                </label>
                <Input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  placeholder="john@example.com"
                  required
                />
              </div>
              <div>
                <label className="block text-gray-700 text-sm font-semibold mb-2">
                  Phone Number
                </label>
                <Input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                  placeholder="0201234567"
                  required
                />
              </div>
            </>
          )}

          {/* Step 3: Password */}
          {step === 3 && (
            <>
              <div>
                <label className="block text-gray-700 text-sm font-semibold mb-2">
                  Password
                </label>
                <Input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  placeholder="Enter password"
                  required
                />
              </div>
              <div>
                <label className="block text-gray-700 text-sm font-semibold mb-2">
                  Confirm Password
                </label>
                <Input
                  type="password"
                  name="password_confirm"
                  value={formData.password_confirm}
                  onChange={handleInputChange}
                  placeholder="Confirm password"
                  required
                />
              </div>
            </>
          )}

          {/* Navigation Buttons */}
          <div className="flex gap-3 pt-4">
            {step > 1 && (
              <Button
                type="button"
                onClick={handlePrevStep}
                variant="outline"
                className="flex-1"
              >
                Back
              </Button>
            )}
            {step < 3 && (
              <Button
                type="button"
                onClick={handleNextStep}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
              >
                Next
              </Button>
            )}
            {step === 3 && (
              <Button
                type="submit"
                disabled={loading}
                className="flex-1 bg-green-600 hover:bg-green-700 text-white"
              >
                {loading ? "Creating Account..." : "Create Account"}
              </Button>
            )}
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
