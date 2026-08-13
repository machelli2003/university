/**
 * Applicant WASSCE Results Entry Page
 * Sections 35-36: WASSCE Manual Verification Entry
 * 
 * Applicant enters:
 * - Examination type
 * - Examination year
 * - Index number
 * - Subject grades
 * 
 * Uploaded evidence/documents shown separately
 */

import React, { useState } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import axios from "axios"

const SUBJECTS = [
  "English",
  "Core Mathematics",
  "Integrated Science",
  "Social Studies",
  "Physics",
  "Chemistry",
  "Biology",
  "Elective Mathematics",
  "Information & Communication Technology",
  "French",
  "Akan",
  "History",
  "Geography",
  "Civic Education",
  "Government",
]

const GRADES = ["A1", "A2", "B1", "B2", "B3", "C1", "C2", "D1", "D2", "D3", "E1", "F1", "F2", "F3"]

export default function ApplicantWASSCEEntryPage() {
  const { schoolCode } = useParams<{ schoolCode: string }>()
  const navigate = useNavigate()

  const [formData, setFormData] = useState({
    examination_type: "WASSCE",
    examination_year: new Date().getFullYear(),
    index_number: "",
    subjects: {} as Record<string, string>,
  })

  const [selectedSubjects, setSelectedSubjects] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const handleAddSubject = (subject: string) => {
    if (!selectedSubjects.includes(subject)) {
      setSelectedSubjects([...selectedSubjects, subject])
      setFormData((prev) => ({
        ...prev,
        subjects: { ...prev.subjects, [subject]: "" },
      }))
    }
  }

  const handleRemoveSubject = (subject: string) => {
    setSelectedSubjects(selectedSubjects.filter((s) => s !== subject))
    const { [subject]: _, ...rest } = formData.subjects
    setFormData((prev) => ({ ...prev, subjects: rest }))
  }

  const handleGradeChange = (subject: string, grade: string) => {
    setFormData((prev) => ({
      ...prev,
      subjects: { ...prev.subjects, [subject]: grade },
    }))
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    if (!formData.index_number) {
      setError("Please enter your index number")
      setLoading(false)
      return
    }

    if (selectedSubjects.length === 0) {
      setError("Please add at least one subject")
      setLoading(false)
      return
    }

    if (selectedSubjects.some((s) => !formData.subjects[s])) {
      setError("Please select a grade for all subjects")
      setLoading(false)
      return
    }

    try {
      const token = localStorage.getItem("access_token")
      const response = await axios.post(
        `/api/v1/apply/${schoolCode}/wassce/submit`,
        {
          examination_type: formData.examination_type,
          examination_year: parseInt(formData.examination_year.toString()),
          index_number: formData.index_number,
          subjects: formData.subjects,
        },
        {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true,
        }
      )

      if (response.data.status === "success") {
        setSuccess(true)
        setTimeout(() => {
          navigate(`/apply/${schoolCode}/dashboard`)
        }, 2000)
      }
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "Failed to submit WASSCE results. Please try again."
      )
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg max-w-md text-center">
          <div className="text-5xl mb-4">✅</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Results Submitted</h2>
          <p className="text-gray-600 mb-6">
            Your WASSCE results have been submitted for verification. Our admissions team will review them and get back to you soon.
          </p>
          <p className="text-sm text-gray-500">Redirecting to dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Enter Your WASSCE Results</h1>
          <p className="text-gray-600">
            Submit your WASSCE examination results for verification. Make sure your information matches your official examination certificate.
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <p className="text-red-700 text-sm">{error}</p>
            </div>
          )}

          {/* Exam Details Section */}
          <div className="mb-8 pb-8 border-b">
            <h2 className="text-xl font-bold text-gray-900 mb-4">📋 Examination Details</h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Examination Type
                </label>
                <select
                  name="examination_type"
                  value={formData.examination_type}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50"
                  disabled
                >
                  <option value="WASSCE">WASSCE</option>
                  <option value="SSSCE">SSSCE</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Examination Year
                </label>
                <select
                  name="examination_year"
                  value={formData.examination_year}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                >
                  {[2024, 2025, 2026].map((year) => (
                    <option key={year} value={year}>
                      {year}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Index Number *
                </label>
                <Input
                  type="text"
                  name="index_number"
                  value={formData.index_number}
                  onChange={handleInputChange}
                  placeholder="e.g., 12345678"
                  required
                />
              </div>
            </div>

            <div className="mt-4 p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-800">
                <strong>💡 Tip:</strong> Your index number should match your WASSCE examination certificate exactly.
              </p>
            </div>
          </div>

          {/* Subjects Section */}
          <div className="mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">🎓 Subjects & Grades</h2>

            {/* Add Subject Dropdown */}
            <div className="mb-6 p-4 bg-gray-50 rounded-lg">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Add Subjects
              </label>
              <select
                onChange={(e) => {
                  if (e.target.value) {
                    handleAddSubject(e.target.value)
                    e.target.value = ""
                  }
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="">Select a subject to add...</option>
                {SUBJECTS.map((subject) => (
                  <option
                    key={subject}
                    value={subject}
                    disabled={selectedSubjects.includes(subject)}
                  >
                    {subject}
                  </option>
                ))}
              </select>
            </div>

            {/* Selected Subjects */}
            {selectedSubjects.length > 0 ? (
              <div className="space-y-3">
                {selectedSubjects.map((subject) => (
                  <div key={subject} className="flex items-center gap-3 p-3 border rounded-lg">
                    <div className="flex-1">
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {subject}
                      </label>
                      <select
                        value={formData.subjects[subject]}
                        onChange={(e) => handleGradeChange(subject, e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md"
                      >
                        <option value="">Select grade...</option>
                        {GRADES.map((grade) => (
                          <option key={grade} value={grade}>
                            {grade}
                          </option>
                        ))}
                      </select>
                    </div>
                    <button
                      type="button"
                      onClick={() => handleRemoveSubject(subject)}
                      className="px-3 py-2 text-red-600 hover:bg-red-50 rounded-md"
                    >
                      Remove
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-4 bg-yellow-50 rounded-lg">
                <p className="text-yellow-800 text-sm">
                  No subjects added yet. Click "Add Subjects" above to start.
                </p>
              </div>
            )}
          </div>

          {/* Evidence Upload Info */}
          <div className="mb-8 pb-8 border-b">
            <h2 className="text-xl font-bold text-gray-900 mb-4">📄 Supporting Evidence</h2>
            <div className="p-4 bg-blue-50 rounded-lg">
              <p className="text-blue-800 text-sm mb-2">
                <strong>Optional:</strong> You can upload a scanned copy of your WASSCE certificate to help verify your results.
              </p>
              <p className="text-blue-700 text-sm">
                This helps our admissions team process your application faster. You can do this in the Documents section.
              </p>
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex gap-3">
            <Button
              type="button"
              onClick={() => navigate(`/apply/${schoolCode}/dashboard`)}
              variant="outline"
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={loading || selectedSubjects.length === 0}
              className="flex-1 bg-blue-600 hover:bg-blue-700"
            >
              {loading ? "Submitting..." : "Submit WASSCE Results"}
            </Button>
          </div>
        </form>

        {/* Help Section */}
        <div className="mt-6 bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-3">❓ Questions?</h3>
          <p className="text-gray-600 text-sm mb-3">
            If you need help entering your WASSCE results, check our FAQs or contact our admissions team.
          </p>
          <Button variant="outline" className="w-full">
            Contact Support
          </Button>
        </div>
      </div>
    </div>
  )
}
