/**
 * Applicant Portal Payment Page
 * Section 34: APPLICANT PORTAL - Payment (FEE-FIRST FLOW)
 * 
 * This page enforces payment BEFORE applicant can access the application form.
 * After successful payment, applicant receives application ID and must reset password on first login.
 */

import React, { useState, useEffect } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { Button } from "@/components/ui/Button"
import axios from "axios"

interface PaymentStatus {
  payment_id: string
  status: string
  amount: number
  reference: string
  created_at: string
  confirmed_at?: string
  receipt_url?: string
}

interface PaymentRequirements {
  payment_required: boolean
  payment_verified: boolean
  application_id?: string
  fee_amount: number
  currency: string
}

export default function ApplicantPortalPaymentPage() {
  const { schoolCode } = useParams<{ schoolCode: string }>()
  const navigate = useNavigate()
  const [applicationId, setApplicationId] = useState("")
  const [amount, setAmount] = useState(150.0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [paymentStatus, setPaymentStatus] = useState<PaymentStatus | null>(null)
  const [paymentInitiated, setPaymentInitiated] = useState(false)
  const [paymentVerified, setPaymentVerified] = useState(false)
  const [step, setStep] = useState(1) // 1: Review, 2: Processing, 3: Success
  const [paystackReference, setPaystackReference] = useState("")

  useEffect(() => {
    // Check payment requirements for this applicant
    const checkPaymentStatus = async () => {
      try {
        const token = localStorage.getItem("access_token")
        if (!token) {
          navigate(`/apply/${schoolCode}/login`)
          return
        }

        // Get payment requirements
        const response = await axios.get(
          `/api/v1/apply/${schoolCode}/payment/requirements`,
          {
            headers: { Authorization: `Bearer ${token}` },
            withCredentials: true,
          }
        )

        const requirements: PaymentRequirements = response.data
        setAmount(requirements.fee_amount)

        // If payment already verified, redirect to dashboard
        if (requirements.payment_verified) {
          setPaymentVerified(true)
          setApplicationId(requirements.application_id || "")
          setTimeout(() => {
            navigate(`/apply/${schoolCode}/dashboard`)
          }, 2000)
        }
      } catch (err: any) {
        if (err.response?.status === 401) {
          navigate(`/apply/${schoolCode}/login`)
        } else {
          console.error("Error checking payment status:", err)
        }
      }
    }

    checkPaymentStatus()
  }, [schoolCode, navigate])

  const handleInitiatePayment = async () => {
    setLoading(true)
    setError(null)

    try {
      const token = localStorage.getItem("access_token")
      const currentUser = JSON.parse(localStorage.getItem("current_user") || "{}")

      const response = await axios.post(
        `/api/v1/apply/${schoolCode}/payment/initiate`,
        {
          application_id: applicationId || "new_application",
          amount: amount,
          email: currentUser.email,
        },
        {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true,
        }
      )

      if (response.data.authorization_url) {
        setPaymentInitiated(true)
        setStep(2)
        
        // Store the payment reference and ID for verification after redirect
        if (response.data.reference) {
          sessionStorage.setItem("payment_reference", response.data.reference)
          sessionStorage.setItem("payment_id", response.data.payment_id)
        }
        
        // Redirect to Paystack
        window.location.href = response.data.authorization_url
      }
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "Failed to initiate payment. Please try again."
      )
    } finally {
      setLoading(false)
    }
  }

  // Check if returning from Paystack
  useEffect(() => {
    const confirmPayment = async () => {
      const reference = sessionStorage.getItem("payment_reference")
      const paymentId = sessionStorage.getItem("payment_id")

      if (reference && paymentId && !paymentVerified) {
        setLoading(true)
        try {
          const token = localStorage.getItem("access_token")
          
          // Confirm payment with backend
          const confirmResponse = await axios.post(
            `/api/v1/apply/${schoolCode}/payment/confirm`,
            {
              paystack_reference: reference,
              payment_id: paymentId,
            },
            {
              headers: { Authorization: `Bearer ${token}` },
              withCredentials: true,
            }
          )

          if (confirmResponse.data.status === "success") {
            setPaymentVerified(true)
            setApplicationId(confirmResponse.data.application_id)
            setStep(3)
            
            // Clean up session storage
            sessionStorage.removeItem("payment_reference")
            sessionStorage.removeItem("payment_id")
            
            // Redirect to dashboard after showing success
            setTimeout(() => {
              navigate(`/apply/${schoolCode}/dashboard`)
            }, 3000)
          }
        } catch (err: any) {
          console.error("Payment confirmation error:", err)
          setError(err.response?.data?.detail || "Payment confirmation failed")
        } finally {
          setLoading(false)
        }
      }
    }

    confirmPayment()
  }, [schoolCode, navigate, paymentVerified])

  if (paymentVerified) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4">
        <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full text-center">
          <div className="mb-4 text-6xl">✓</div>
          <h1 className="text-3xl font-bold text-green-600 mb-2">Payment Successful!</h1>
          <p className="text-gray-700 mb-4">
            Your application is now active. Your application ID is <span className="font-mono font-bold">{applicationId}</span>
          </p>
          <p className="text-gray-600 text-sm mb-6">
            Redirecting to your dashboard...
          </p>
          <Button
            onClick={() => navigate(`/apply/${schoolCode}/dashboard`)}
            className="w-full"
          >
            Go to Dashboard
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4">
      <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Application Fee Payment</h1>
        <p className="text-gray-600 mb-6">
          Step {step} of 3: {step === 1 ? "Review Fee" : step === 2 ? "Processing Payment" : "Confirm Payment"}
        </p>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}

        {/* Step 1: Review Payment */}
        {step === 1 && (
          <div className="space-y-4">
            <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
              <p className="text-gray-700 text-sm font-medium">Application Fee</p>
              <p className="text-4xl font-bold text-blue-600 mt-2">₦{amount.toFixed(2)}</p>
              <p className="text-gray-600 text-xs mt-2">
                One-time payment to activate your application
              </p>
            </div>

            <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
              <p className="text-gray-700 text-sm mb-2"><strong>What's included:</strong></p>
              <ul className="text-gray-600 text-xs space-y-1">
                <li>✓ Application ID assignment</li>
                <li>✓ Portal access</li>
                <li>✓ Application form submission</li>
                <li>✓ Results verification</li>
              </ul>
            </div>

            <Button
              onClick={handleInitiatePayment}
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white"
            >
              {loading ? "Processing..." : "Proceed to Payment"}
            </Button>
          </div>
        )}

        {/* Step 2: Processing */}
        {step === 2 && (
          <div className="text-center space-y-4">
            <div className="inline-block">
              <div className="animate-spin">
                <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full"></div>
              </div>
            </div>
            <p className="text-gray-700">
              Redirecting you to Paystack for secure payment...
            </p>
            <p className="text-gray-600 text-sm">
              Please do not close this window
            </p>
          </div>
        )}

        {/* Step 3: Success (shown while redirecting) */}
        {step === 3 && (
          <div className="text-center space-y-4">
            <div className="text-6xl">✓</div>
            <p className="text-gray-700 font-semibold">Payment Confirmed!</p>
            <p className="text-gray-600 text-sm">
              Your application is now active.
            </p>
            <p className="text-gray-600 text-sm">
              Redirecting to your dashboard...
            </p>
          </div>
        )}

        <p className="text-center text-gray-600 text-xs mt-6">
          Secure payment powered by Paystack
        </p>
      </div>
    </div>
  )
}
