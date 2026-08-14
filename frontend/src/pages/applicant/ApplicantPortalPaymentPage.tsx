/**
 * Applicant Portal Payment Page
 * Section 34: APPLICANT PORTAL - Payment
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

export default function ApplicantPortalPaymentPage() {
  const { schoolCode } = useParams<{ schoolCode: string }>()
  const navigate = useNavigate()
  const [applicationId, setApplicationId] = useState("")
  const [amount, setAmount] = useState(150.0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [paymentStatus, setPaymentStatus] = useState<PaymentStatus | null>(null)
  const [paymentInitiated, setPaymentInitiated] = useState(false)
  const [step, setStep] = useState(1) // 1: Review, 2: Processing, 3: Status

  useEffect(() => {
    // Fetch application and payment details
    const fetchApplicationDetails = async () => {
      try {
        const token = localStorage.getItem("access_token")
        const response = await axios.get(
          `/api/v1/apply/${schoolCode}/application/status`,
          {
            headers: { Authorization: `Bearer ${token}` },
            withCredentials: true,
          }
        )
        setApplicationId(response.data.application_id || "")
        setAmount(response.data.payment_amount || 150.0)
      } catch (err: any) {
        if (err.response?.status === 401) {
          navigate(`/apply/${schoolCode}/login`)
        }
      }
    }

    fetchApplicationDetails()
  }, [schoolCode, navigate])

  const handleInitiatePayment = async () => {
    if (!applicationId) {
      setError("No application found. Please submit your application first.")
      return
    }

    setLoading(true)
    setError(null)

    try {
      const token = localStorage.getItem("access_token")
      const currentUser = JSON.parse(localStorage.getItem("current_user") || "{}")

      const response = await axios.post(
        `/api/v1/apply/${schoolCode}/payment/initiate`,
        {
          application_id: applicationId,
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

  const handleCheckPaymentStatus = async () => {
    if (!paymentStatus?.payment_id) {
      setError("Payment ID not found")
      return
    }

    setLoading(true)

    try {
      const token = localStorage.getItem("access_token")
      const response = await axios.get(
        `/api/v1/apply/${schoolCode}/payment/status/${paymentStatus.payment_id}`,
        {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true,
        }
      )

      setPaymentStatus(response.data)
      setStep(3)

      if (response.data.status === "confirmed") {
        setTimeout(() => {
          navigate(`/apply/${schoolCode}/dashboard`)
        }, 3000)
      }
    } catch (err: any) {
      setError("Failed to check payment status")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4">
      <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Application Fee Payment</h1>
        <p className="text-gray-600 mb-6">
          Step {step} of 3: {step === 1 ? "Review Fee" : step === 2 ? "Processing" : "Confirm Payment"}
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
                This fee is required to process your application. You will receive a receipt after successful payment.
              </p>
            </div>

            <div className="bg-gray-50 p-4 rounded-lg space-y-2">
              <h3 className="font-semibold text-gray-900">Payment Details:</h3>
              <div className="flex justify-between text-sm text-gray-700">
                <span>Amount:</span>
                <span className="font-medium">₦{amount.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-sm text-gray-700">
                <span>Method:</span>
                <span className="font-medium">Paystack</span>
              </div>
              <div className="flex justify-between text-sm text-gray-700">
                <span>Status:</span>
                <span className="font-medium text-yellow-600">Pending</span>
              </div>
            </div>

            <div className="bg-blue-50 p-4 rounded-lg text-sm">
              <p className="text-blue-900">
                ✓ Your payment information is secure and encrypted. We use Paystack for secure payment processing.
              </p>
            </div>

            <Button
              onClick={handleInitiatePayment}
              disabled={loading || !applicationId}
              className="w-full bg-blue-600 hover:bg-blue-700"
            >
              {loading ? "Processing..." : "Proceed to Payment"}
            </Button>

            <Button
              onClick={() => navigate(`/apply/${schoolCode}/application`)}
              variant="outline"
              className="w-full"
            >
              Back to Application
            </Button>
          </div>
        )}

        {/* Step 2: Processing */}
        {step === 2 && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
            <p className="text-gray-600 font-medium">Redirecting to Paystack...</p>
            <p className="text-gray-500 text-sm mt-2">
              Please do not close this page while payment is processing
            </p>
          </div>
        )}

        {/* Step 3: Payment Status */}
        {step === 3 && paymentStatus && (
          <div className="space-y-4">
            {paymentStatus.status === "confirmed" ? (
              <>
                <div className="bg-green-50 p-6 rounded-lg border border-green-200 text-center">
                  <p className="text-4xl mb-2">✓</p>
                  <p className="text-green-900 font-bold text-lg">Payment Successful!</p>
                  <p className="text-green-800 text-sm mt-2">
                    Your payment has been confirmed. A receipt has been sent to your email.
                  </p>
                </div>

                <div className="bg-gray-50 p-4 rounded-lg space-y-2">
                  <h3 className="font-semibold text-gray-900">Payment Confirmation:</h3>
                  <div className="flex justify-between text-sm text-gray-700">
                    <span>Reference:</span>
                    <span className="font-mono text-xs">{paymentStatus.reference}</span>
                  </div>
                  <div className="flex justify-between text-sm text-gray-700">
                    <span>Amount:</span>
                    <span className="font-medium">₦{paymentStatus.amount.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-sm text-gray-700">
                    <span>Confirmed:</span>
                    <span className="font-medium">
                      {paymentStatus.confirmed_at ? new Date(paymentStatus.confirmed_at).toLocaleDateString() : "N/A"}
                    </span>
                  </div>
                </div>

                {paymentStatus.receipt_url && (
                  <a
                    href={paymentStatus.receipt_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block text-center text-blue-600 hover:text-blue-700 font-medium text-sm"
                  >
                    📄 Download Receipt
                  </a>
                )}

                <p className="text-center text-gray-600 text-sm">
                  Redirecting to dashboard in 3 seconds...
                </p>

                <Button
                  onClick={() => navigate(`/apply/${schoolCode}/dashboard`)}
                  className="w-full bg-green-600 hover:bg-green-700"
                >
                  Go to Dashboard
                </Button>
              </>
            ) : (
              <>
                <div className="bg-yellow-50 p-6 rounded-lg border border-yellow-200 text-center">
                  <p className="text-yellow-900 font-bold">Payment Pending</p>
                  <p className="text-yellow-800 text-sm mt-2">
                    Your payment is being processed. This may take a few moments.
                  </p>
                </div>

                <Button
                  onClick={handleCheckPaymentStatus}
                  disabled={loading}
                  className="w-full bg-blue-600 hover:bg-blue-700"
                >
                  {loading ? "Checking..." : "Check Status"}
                </Button>

                <Button
                  onClick={() => navigate(`/apply/${schoolCode}/dashboard`)}
                  variant="outline"
                  className="w-full"
                >
                  Continue to Dashboard
                </Button>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
