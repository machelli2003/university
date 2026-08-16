/**
 * Application Form Purchase Page
 * Ghana University Model - PIN & Serial Number Purchase
 * 
 * In Ghana universities, applicants must:
 * 1. Purchase an application form (PIN + Serial number)
 * 2. Receive credentials via email
 * 3. Use PIN + Serial to login to the application portal
 * 4. Then fill out the admission form
 * 
 * This page handles step 1: Purchase and payment
 */

import React, { useState, useEffect } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { Button } from "@/components/ui/Button"
import axios from "axios"
import { AlertCircle, CheckCircle, Copy, Eye, EyeOff } from "lucide-react"

interface CredentialsData {
  pin: string
  serial_number: string
  payment_reference: string
}

type PageStep = "info" | "payment" | "verification" | "success"

export default function ApplicationFormPurchasePage() {
  const { schoolCode } = useParams<{ schoolCode: string }>()
  const navigate = useNavigate()
  
  // Form state
  const [formData, setFormData] = useState({
    email: "",
    first_name: "",
    last_name: "",
    phone_number: "",
    admissionCycleId: "2024/2025",
  })
  
  // Payment state
  const [amount, setAmount] = useState(50.0) // GHS
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  
  // Step navigation
  const [step, setStep] = useState<PageStep>("info")
  
  // Payment tracking
  const [paymentReference, setPaymentReference] = useState<string | null>(null)
  
  // Credentials after payment
  const [credentials, setCredentials] = useState<CredentialsData | null>(null)
  const [showPin, setShowPin] = useState(false)
  const [showSerial, setShowSerial] = useState(false)
  const [copiedField, setCopiedField] = useState<string | null>(null)

  // Validate form
  const isFormValid = () => {
    return (
      formData.email &&
      formData.first_name &&
      formData.last_name &&
      formData.phone_number &&
      formData.email.includes("@")
    )
  }

  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  // Step 1: Submit applicant info and initiate payment
  const handlePurchaseForm = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!isFormValid()) {
      setError("Please fill in all required fields with valid information")
      return
    }

    setLoading(true)
    setError(null)

    try {
      // Call backend to initialize payment
      const response = await axios.post(
        "/api/v1/application-form/purchase",
        {
          email: formData.email,
          first_name: formData.first_name,
          last_name: formData.last_name,
          phone_number: formData.phone_number,
          admission_cycle_id: formData.admissionCycleId,
        }
      )

      const { payment_url, reference } = response.data

      // Store reference for later verification
      setPaymentReference(reference)
      
      // Show verification step (we'll check payment status)
      setStep("payment")
      
      // In production, redirect to Paystack
      // window.location.href = payment_url
      
      // For demo, show the payment URL
      localStorage.setItem("pending_payment_reference", reference)
      localStorage.setItem("applicant_email", formData.email)

      // Simulate opening Paystack in a new window
      // window.open(payment_url, "_blank")
      
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || "Failed to initiate payment"
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  // Step 2: Verify payment and get credentials
  const handleVerifyPayment = async () => {
    if (!paymentReference) {
      setError("No payment reference found")
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await axios.post(
        "/api/v1/application-form/verify-payment",
        {
          reference: paymentReference,
        }
      )

      if (response.data.success && response.data.credentials) {
        setCredentials(response.data.credentials)
        setSuccess(true)
        setStep("success")
        
        // Clear the pending reference
        localStorage.removeItem("pending_payment_reference")
      } else {
        setError(response.data.message || "Payment verification failed")
      }
      
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || "Failed to verify payment"
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  // Copy to clipboard
  const handleCopy = (text: string, field: string) => {
    navigator.clipboard.writeText(text)
    setCopiedField(field)
    setTimeout(() => setCopiedField(null), 2000)
  }

  // Render step 1: Application form info
  if (step === "info") {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
        <div className="max-w-md mx-auto">
          <div className="bg-white rounded-lg shadow-lg p-8">
            {/* Header */}
            <div className="mb-8 text-center">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Purchase Application Form
              </h1>
              <p className="text-gray-600">
                Get your PIN and Serial Number to access the application portal
              </p>
            </div>

            {/* Error Alert */}
            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex gap-3">
                <AlertCircle className="text-red-600 flex-shrink-0" size={20} />
                <p className="text-red-800 text-sm">{error}</p>
              </div>
            )}

            {/* Form */}
            <form onSubmit={handlePurchaseForm} className="space-y-4">
              {/* Email */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email Address
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                  placeholder="your.email@example.com"
                  required
                />
              </div>

              {/* First Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  First Name
                </label>
                <input
                  type="text"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                  placeholder="John"
                  required
                />
              </div>

              {/* Last Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Last Name
                </label>
                <input
                  type="text"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                  placeholder="Doe"
                  required
                />
              </div>

              {/* Phone */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Phone Number
                </label>
                <input
                  type="tel"
                  name="phone_number"
                  value={formData.phone_number}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                  placeholder="+233 XX XXX XXXX"
                  required
                />
              </div>

              {/* Amount Display */}
              <div className="bg-indigo-50 p-4 rounded-lg">
                <div className="flex justify-between items-center">
                  <span className="text-gray-700 font-medium">Application Fee:</span>
                  <span className="text-2xl font-bold text-indigo-600">
                    ₵{amount.toFixed(2)}
                  </span>
                </div>
              </div>

              {/* Submit Button */}
              <Button
                type="submit"
                disabled={!isFormValid() || loading}
                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-2 rounded-lg font-medium disabled:opacity-50"
              >
                {loading ? "Processing..." : "Proceed to Payment"}
              </Button>

              {/* Alternative Login */}
              <div className="text-center pt-4 border-t">
                <p className="text-gray-600 text-sm mb-2">
                  Already have PIN and Serial?
                </p>
                <Button
                  type="button"
                  onClick={() => navigate(`/auth/login/application-form`)}
                  className="w-full bg-white border border-indigo-600 text-indigo-600 hover:bg-indigo-50 py-2 rounded-lg font-medium"
                >
                  Login with Credentials
                </Button>
              </div>
            </form>
          </div>
        </div>
      </div>
    )
  }

  // Render step 2: Payment verification
  if (step === "payment") {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
        <div className="max-w-md mx-auto">
          <div className="bg-white rounded-lg shadow-lg p-8">
            {/* Header */}
            <div className="mb-8 text-center">
              <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-yellow-600 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Processing Payment
              </h2>
              <p className="text-gray-600">
                Your payment is being verified...
              </p>
            </div>

            {/* Info */}
            <div className="bg-blue-50 p-4 rounded-lg mb-6">
              <p className="text-sm text-gray-700">
                <strong>Reference:</strong> {paymentReference}
              </p>
            </div>

            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex gap-3">
                <AlertCircle className="text-red-600 flex-shrink-0" size={20} />
                <div>
                  <p className="text-red-800 text-sm font-medium mb-2">{error}</p>
                  <Button
                    onClick={() => setStep("info")}
                    className="text-red-600 hover:text-red-700 text-sm font-medium"
                  >
                    Try Again
                  </Button>
                </div>
              </div>
            )}

            <Button
              onClick={handleVerifyPayment}
              disabled={loading}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-2 rounded-lg font-medium disabled:opacity-50"
            >
              {loading ? "Verifying..." : "Verify Payment"}
            </Button>
          </div>
        </div>
      </div>
    )
  }

  // Render step 3: Success - Show credentials
  if (step === "success" && credentials) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 py-12 px-4">
        <div className="max-w-md mx-auto">
          <div className="bg-white rounded-lg shadow-lg p-8">
            {/* Success Header */}
            <div className="mb-8 text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Payment Successful!
              </h1>
              <p className="text-gray-600">
                Your application form has been purchased
              </p>
            </div>

            {/* Credentials Section */}
            <div className="space-y-6">
              {/* PIN */}
              <div className="bg-gradient-to-br from-indigo-50 to-blue-50 p-6 rounded-lg border border-indigo-200">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Your PIN
                </label>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-white px-4 py-3 rounded-lg border border-gray-300">
                    <code className="text-lg font-mono font-bold text-gray-900">
                      {showPin ? credentials.pin : "••••••"}
                    </code>
                  </div>
                  <button
                    onClick={() => setShowPin(!showPin)}
                    className="p-2 hover:bg-white rounded-lg border border-gray-300"
                  >
                    {showPin ? <EyeOff size={20} /> : <Eye size={20} />}
                  </button>
                  <button
                    onClick={() => handleCopy(credentials.pin, "pin")}
                    className="p-2 hover:bg-white rounded-lg border border-gray-300"
                  >
                    <Copy size={20} className={copiedField === "pin" ? "text-green-600" : "text-gray-600"} />
                  </button>
                </div>
              </div>

              {/* Serial Number */}
              <div className="bg-gradient-to-br from-purple-50 to-pink-50 p-6 rounded-lg border border-purple-200">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Your Serial Number
                </label>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-white px-4 py-3 rounded-lg border border-gray-300">
                    <code className="text-lg font-mono font-bold text-gray-900">
                      {showSerial ? credentials.serial_number : "••••••••"}
                    </code>
                  </div>
                  <button
                    onClick={() => setShowSerial(!showSerial)}
                    className="p-2 hover:bg-white rounded-lg border border-gray-300"
                  >
                    {showSerial ? <EyeOff size={20} /> : <Eye size={20} />}
                  </button>
                  <button
                    onClick={() => handleCopy(credentials.serial_number, "serial")}
                    className="p-2 hover:bg-white rounded-lg border border-gray-300"
                  >
                    <Copy size={20} className={copiedField === "serial" ? "text-green-600" : "text-gray-600"} />
                  </button>
                </div>
              </div>

              {/* Payment Reference */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <label className="block text-xs font-medium text-gray-600 mb-1">
                  Payment Reference
                </label>
                <code className="text-sm text-gray-900">{credentials.payment_reference}</code>
              </div>
            </div>

            {/* Important Notice */}
            <div className="mt-8 p-4 bg-amber-50 border border-amber-200 rounded-lg">
              <p className="text-sm text-amber-800">
                <strong>⚠️ Important:</strong> Keep your PIN and Serial Number safe. You will need them to login to the application portal. An email has been sent to your registered address with these credentials.
              </p>
            </div>

            {/* Login Button */}
            <Button
              onClick={() => navigate(`/auth/login/application-form`)}
              className="w-full mt-8 bg-indigo-600 hover:bg-indigo-700 text-white py-2 rounded-lg font-medium"
            >
              Proceed to Login
            </Button>

            {/* Home Link */}
            <div className="text-center mt-4">
              <Button
                onClick={() => navigate("/")}
                className="text-indigo-600 hover:text-indigo-700 text-sm font-medium"
              >
                Back to Home
              </Button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return null
}
