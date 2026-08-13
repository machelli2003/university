/**
 * Applicant Portal Landing Page
 * Section 33-34: University Application URL & Applicant Portal
 * 
 * Displays university information and allows applicant to login/register
 * Accessed via app.universityplatform.com/apply/:schoolCode
 */

import React, { useState, useEffect } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { Button } from "@/components/ui/Button"
import axios from "axios"

interface UniversityInfo {
  display_name: string
  legal_name: string
  school_code: string
  logo_url?: string
  primary_color: string
  secondary_color: string
  website?: string
  contact_email?: string
  contact_phone?: string
}

export default function ApplicantPortalLandingPage() {
  const { schoolCode } = useParams<{ schoolCode: string }>()
  const navigate = useNavigate()
  const [universityInfo, setUniversityInfo] = useState<UniversityInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchUniversityInfo = async () => {
      try {
        if (!schoolCode) {
          setError("University code not provided")
          return
        }

        const response = await axios.get(
          `/api/v1/apply/${schoolCode.toLowerCase()}`,
          { withCredentials: true }
        )
        setUniversityInfo(response.data)
        setError(null)
      } catch (err: any) {
        setError(
          err.response?.data?.detail ||
          "Failed to load university information. Please check the university code and try again."
        )
        console.error("Error fetching university info:", err)
      } finally {
        setLoading(false)
      }
    }

    fetchUniversityInfo()
  }, [schoolCode])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading university portal...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="bg-white p-8 rounded-lg shadow-lg max-w-md">
          <div className="text-center">
            <div className="text-red-500 text-5xl mb-4">⚠️</div>
            <h1 className="text-2xl font-bold text-gray-900 mb-4">Portal Not Available</h1>
            <p className="text-gray-600 mb-6">{error}</p>
            <Button onClick={() => window.location.href = "/"} className="w-full">
              Return Home
            </Button>
          </div>
        </div>
      </div>
    )
  }

  if (!universityInfo) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <p className="text-gray-600">No university information available</p>
        </div>
      </div>
    )
  }

  return (
    <div
      className="min-h-screen"
      style={{
        background: `linear-gradient(135deg, ${universityInfo.primary_color}20 0%, ${universityInfo.secondary_color}20 100%)`,
      }}
    >
      {/* Header with University Logo/Name */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8 flex items-center justify-between">
          {universityInfo.logo_url && (
            <img
              src={universityInfo.logo_url}
              alt={universityInfo.display_name}
              className="h-12"
            />
          )}
          <h1 className="text-3xl font-bold text-gray-900">{universityInfo.display_name}</h1>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Left Column - Welcome Message */}
          <div className="flex flex-col justify-center">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Welcome to {universityInfo.display_name}
            </h2>
            <p className="text-xl text-gray-600 mb-8">
              Apply for admission to {universityInfo.display_name} through this portal.
              Access your application status, submit documents, and receive admission decisions.
            </p>
            <div className="space-y-3 text-gray-700 mb-8">
              <div className="flex items-start">
                <span className="text-2xl mr-3">✓</span>
                <span>Complete online application form</span>
              </div>
              <div className="flex items-start">
                <span className="text-2xl mr-3">✓</span>
                <span>Upload required documents</span>
              </div>
              <div className="flex items-start">
                <span className="text-2xl mr-3">✓</span>
                <span>Track your application status in real-time</span>
              </div>
              <div className="flex items-start">
                <span className="text-2xl mr-3">✓</span>
                <span>Receive admission offers and decisions</span>
              </div>
            </div>
          </div>

          {/* Right Column - Auth Buttons */}
          <div className="flex flex-col justify-center space-y-4">
            <div className="bg-white rounded-lg shadow-lg p-8">
              <h3 className="text-2xl font-bold text-gray-900 mb-6">Get Started</h3>

              <div className="space-y-4">
                <Button
                  onClick={() => navigate(`/apply/${schoolCode}/login`)}
                  className="w-full py-3 text-lg"
                  style={{
                    backgroundColor: universityInfo.primary_color,
                  }}
                >
                  Sign In to Your Account
                </Button>

                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-gray-300"></div>
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-2 bg-white text-gray-500">Don't have an account?</span>
                  </div>
                </div>

                <Button
                  onClick={() => navigate(`/apply/${schoolCode}/register`)}
                  variant="outline"
                  className="w-full py-3 text-lg border-2"
                  style={{
                    borderColor: universityInfo.primary_color,
                    color: universityInfo.primary_color,
                  }}
                >
                  Create New Application
                </Button>
              </div>

              <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                <p className="text-sm text-gray-600">
                  <strong>First time here?</strong> Click "Create New Application" to start your application.
                  You'll create an account and begin the application process.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="bg-gray-900 text-white mt-12">
        <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h4 className="text-lg font-bold mb-4">Contact Information</h4>
              {universityInfo.contact_email && (
                <p className="text-gray-300 mb-2">
                  Email: <a href={`mailto:${universityInfo.contact_email}`} className="text-blue-400 hover:text-blue-300">
                    {universityInfo.contact_email}
                  </a>
                </p>
              )}
              {universityInfo.contact_phone && (
                <p className="text-gray-300">
                  Phone: <a href={`tel:${universityInfo.contact_phone}`} className="text-blue-400 hover:text-blue-300">
                    {universityInfo.contact_phone}
                  </a>
                </p>
              )}
            </div>
            <div>
              <h4 className="text-lg font-bold mb-4">Quick Links</h4>
              {universityInfo.website && (
                <p className="text-gray-300 mb-2">
                  <a href={universityInfo.website} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300">
                    Visit University Website →
                  </a>
                </p>
              )}
              <p className="text-gray-300">
                <a href="/" className="text-blue-400 hover:text-blue-300">
                  Back to Home →
                </a>
              </p>
            </div>
            <div>
              <h4 className="text-lg font-bold mb-4">Need Help?</h4>
              <p className="text-gray-300 mb-2">
                Check our <a href="#" className="text-blue-400 hover:text-blue-300">FAQs</a>
              </p>
              <p className="text-gray-300">
                Contact <a href="mailto:support@universityplatform.com" className="text-blue-400 hover:text-blue-300">
                  support
                </a>
              </p>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-gray-800 text-center text-gray-400">
            <p>&copy; 2024 Enterprise University Management Platform. All rights reserved.</p>
          </div>
        </div>
      </div>
    </div>
  )
}
