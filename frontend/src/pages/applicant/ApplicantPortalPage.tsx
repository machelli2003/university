import { useEffect, useState } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { Button } from "@/components/ui/Button"
import { onboardingApi } from "@/services/api/onboarding"
import { getErrorMessage } from "@/services/api/client"
import { AlertCircle, CheckCircle2, FileText, Upload } from "lucide-react"

export default function ApplicantPortalPage() {
  const { schoolCode } = useParams<{ schoolCode: string }>()
  const navigate = useNavigate()
  const [university, setUniversity] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadUniversityInfo()
  }, [schoolCode])

  async function loadUniversityInfo() {
    try {
      // In production, fetch by school code
      // For now, load the demo application to get university details
      const data = await onboardingApi.getApplication("UAPP-2026-000001")
      setUniversity(data)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="p-8 text-center">Loading...</div>
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="rounded border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-cocoa-50 to-white">
      <div className="max-w-4xl mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-ink mb-2">{university?.display_name || "University"}</h1>
          <p className="text-lg text-cocoa-600">Apply for Admission</p>
        </div>

        {/* Welcome Card */}
        <div className="rounded-lg bg-white border border-cocoa-100 shadow-sm p-8 mb-8">
          <h2 className="text-2xl font-semibold text-ink mb-4">Welcome to the Applicant Portal</h2>
          <p className="text-cocoa-600 mb-6">
            Follow the steps below to complete your application for {university?.display_name || "this university"}.
          </p>

          <div className="grid md:grid-cols-4 gap-4">
            <StepCard
              number={1}
              title="Create Account"
              description="Register for your applicant account"
              completed={false}
              onClick={() => navigate(`/apply/${schoolCode}/register`)}
            />
            <StepCard
              number={2}
              title="Personal Info"
              description="Provide your personal details"
              completed={false}
              onClick={() => navigate(`/apply/${schoolCode}/dashboard`)}
            />
            <StepCard
              number={3}
              title="Academic Info"
              description="Enter your academic background"
              completed={false}
              onClick={() => navigate(`/apply/${schoolCode}/dashboard`)}
            />
            <StepCard
              number={4}
              title="Submit"
              description="Review and submit application"
              completed={false}
              onClick={() => navigate(`/apply/${schoolCode}/dashboard`)}
            />
          </div>
        </div>

        {/* Quick Info */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <InfoCard
            title="Application Fee"
            value={`₦${university?.application_fee || "Contact university"}`}
            icon="💳"
          />
          <InfoCard
            title="Closing Date"
            value="Check website for exact date"
            icon="📅"
          />
          <InfoCard
            title="Available Programmes"
            value={`${15} Programmes`}
            icon="🎓"
          />
        </div>

        {/* CTA Buttons */}
        <div className="flex gap-4 justify-center">
          <Button onClick={() => navigate(`/apply/${schoolCode}/register`)} variant="primary">
            Start New Application
          </Button>
          <Button onClick={() => navigate(`/apply/${schoolCode}/login`)} variant="secondary">
            Sign In
          </Button>
        </div>
      </div>
    </div>
  )
}

function StepCard({
  number,
  title,
  description,
  completed,
  onClick,
}: {
  number: number
  title: string
  description: string
  completed: boolean
  onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      className="p-4 rounded-lg border border-cocoa-100 bg-white hover:shadow-md hover:border-cocoa-300 transition text-left"
    >
      <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-white mb-2 ${
        completed ? "bg-green-500" : "bg-cocoa-600"
      }`}>
        {completed ? <CheckCircle2 className="h-5 w-5" /> : number}
      </div>
      <h3 className="font-medium text-ink">{title}</h3>
      <p className="text-sm text-cocoa-600">{description}</p>
    </button>
  )
}

function InfoCard({
  title,
  value,
  icon,
}: {
  title: string
  value: string
  icon: string
}) {
  return (
    <div className="rounded-lg bg-white border border-cocoa-100 p-6 text-center">
      <div className="text-3xl mb-2">{icon}</div>
      <h3 className="font-medium text-ink mb-1">{title}</h3>
      <p className="text-cocoa-600">{value}</p>
    </div>
  )
}
