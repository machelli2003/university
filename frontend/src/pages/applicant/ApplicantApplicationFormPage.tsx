/**
 * Applicant Portal Application Form Page
 * Route: /apply/:schoolCode/application
 *
 * Allows applicants to complete and submit their university application form:
 * - Personal Information
 * - WASSCE Results & Grades
 * - Programme Choice Selection (1st, 2nd, 3rd choices)
 * - Statement of Purpose & Special Needs Declaration
 */

import React, { useState, useEffect } from "react"
import { useParams, useNavigate, useSearchParams } from "react-router-dom"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import axios from "axios"

interface Programme {
  id: string
  code: string
  name: string
  duration_years: number
  description?: string
}

interface SubjectGrade {
  subject: string
  grade: string
}

const WASSCE_SUBJECTS = [
  "Core Mathematics",
  "English Language",
  "Integrated Science",
  "Social Studies",
  "Elective Mathematics",
  "Physics",
  "Chemistry",
  "Biology",
  "Economics",
  "Geography",
  "Government",
  "History",
  "Accounting",
  "Business Management",
  "Costing",
  "General Knowledge in Art",
  "Management in Living",
  "Food and Nutrition",
]

const GRADE_VALUES: Record<string, number> = {
  A1: 1,
  B2: 2,
  B3: 3,
  C4: 4,
  C5: 5,
  C6: 6,
  D7: 7,
  E8: 8,
  F9: 9,
}

export default function ApplicantApplicationFormPage() {
  const { schoolCode } = useParams<{ schoolCode: string }>()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const tabParam = searchParams.get("tab")
  const defaultTab = (tabParam === "statement" || tabParam === "academic" || tabParam === "programmes") ? tabParam : "personal"

  const [activeTab, setActiveTab] = useState<"personal" | "academic" | "programmes" | "statement">(defaultTab)
  const [loading, setLoading] = useState(false)
  const [fetching, setFetching] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [successMsg, setSuccessMsg] = useState<string | null>(null)

  // University programmes list
  const [programmes, setProgrammes] = useState<Programme[]>([])

  // Form State
  const [personalInfo, setPersonalInfo] = useState({
    first_name: "",
    last_name: "",
    date_of_birth: "",
    gender: "Male",
    phone: "",
    address: "",
    city: "",
    region: "Greater Accra",
    nationality: "Ghanaian",
  })

  const [academicInfo, setAcademicInfo] = useState({
    wassce_year: new Date().getFullYear(),
    wassce_index_number: "",
    wassce_center: "",
    subjects: [
      { subject: "Core Mathematics", grade: "A1" },
      { subject: "English Language", grade: "A1" },
      { subject: "Integrated Science", grade: "A1" },
      { subject: "Social Studies", grade: "B2" },
    ] as SubjectGrade[],
  })

  const [programmeChoices, setProgrammeChoices] = useState({
    choice_1: "",
    choice_2: "",
    choice_3: "",
  })

  const [additionalInfo, setAdditionalInfo] = useState({
    statement_of_purpose: "",
    special_needs: "",
    disability_declaration: "None",
  })

  // Computed WASSCE aggregate
  const calculateAggregate = () => {
    const grades = academicInfo.subjects
      .map((s) => GRADE_VALUES[s.grade] || 9)
      .sort((a, b) => a - b)
    return grades.slice(0, 6).reduce((sum, val) => sum + val, 0)
  }

  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = localStorage.getItem("access_token")
        if (!token) {
          navigate(`/apply/${schoolCode}/login`)
          return
        }

        // Fetch programmes list
        const progRes = await axios.get(`/api/v1/apply/${schoolCode}/programmes`)
        setProgrammes(progRes.data || [])

        if (progRes.data && progRes.data.length > 0) {
          setProgrammeChoices({
            choice_1: progRes.data[0]?.code || progRes.data[0]?.id || "",
            choice_2: progRes.data[1]?.code || progRes.data[1]?.id || "",
            choice_3: progRes.data[2]?.code || progRes.data[2]?.id || "",
          })
        }

        // Fetch existing applicant profile if available
        try {
          const profileRes = await axios.get(`/api/v1/apply/${schoolCode}/application`, {
            headers: { Authorization: `Bearer ${token}` },
          })
          if (profileRes.data) {
            const data = profileRes.data
            setPersonalInfo({
              first_name: data.first_name || "",
              last_name: data.last_name || "",
              date_of_birth: data.date_of_birth ? data.date_of_birth.split("T")[0] : "",
              gender: data.gender || "Male",
              phone: data.phone || "",
              address: data.address || "",
              city: data.city || "",
              region: data.region || "Greater Accra",
              nationality: data.nationality || "Ghanaian",
            })

            if (data.results && Object.keys(data.results).length > 0) {
              const loadedSubjects: SubjectGrade[] = Object.entries(data.results).map(
                ([subj, grd]) => ({ subject: subj, grade: String(grd) })
              )
              setAcademicInfo({
                wassce_year: data.exam_year || new Date().getFullYear(),
                wassce_index_number: data.index_number || "",
                wassce_center: "",
                subjects: loadedSubjects,
              })
            }

            if (data.programme_choices && data.programme_choices.length > 0) {
              setProgrammeChoices({
                choice_1: data.programme_choices[0]?.programme_code || "",
                choice_2: data.programme_choices[1]?.programme_code || "",
                choice_3: data.programme_choices[2]?.programme_code || "",
              })
            }

            if (data.statement_of_purpose || data.special_needs || data.disability_declaration) {
              setAdditionalInfo({
                statement_of_purpose: data.statement_of_purpose || "",
                special_needs: data.special_needs || "",
                disability_declaration: data.disability_declaration || "None",
              })
            }
          }
        } catch {
          // Draft not submitted yet
        }
      } catch (err: any) {
        console.error("Error loading application data:", err)
      } finally {
        setFetching(false)
      }
    }

    fetchData()
  }, [schoolCode, navigate])

  const handleAddSubject = () => {
    if (academicInfo.subjects.length >= 10) return
    setAcademicInfo((prev) => ({
      ...prev,
      subjects: [...prev.subjects, { subject: WASSCE_SUBJECTS[0], grade: "C4" }],
    }))
  }

  const handleRemoveSubject = (index: number) => {
    if (academicInfo.subjects.length <= 4) return
    setAcademicInfo((prev) => ({
      ...prev,
      subjects: prev.subjects.filter((_, i) => i !== index),
    }))
  }

  const handleSubjectChange = (index: number, field: "subject" | "grade", value: string) => {
    const updated = [...academicInfo.subjects]
    updated[index][field] = value
    setAcademicInfo((prev) => ({ ...prev, subjects: updated }))
  }

  const handleSubmitApplication = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setSuccessMsg(null)

    try {
      const token = localStorage.getItem("access_token")

      // Format subjects into dictionary
      const subjectsMap: Record<string, string> = {}
      academicInfo.subjects.forEach((item) => {
        subjectsMap[item.subject] = item.grade
      })

      // 1. Update personal info
      await axios.put(
        `/api/v1/apply/${schoolCode}/personal`,
        personalInfo,
        { headers: { Authorization: `Bearer ${token}` } }
      )

      // 2. Submit application form
      const payload = {
        wassce_year: Number(academicInfo.wassce_year),
        wassce_index_number: academicInfo.wassce_index_number,
        wassce_center: academicInfo.wassce_center,
        subjects_and_grades: subjectsMap,
        aggregate: calculateAggregate(),
        choice_1_programme_code: programmeChoices.choice_1,
        choice_2_programme_code: programmeChoices.choice_2 || undefined,
        choice_3_programme_code: programmeChoices.choice_3 || undefined,
        statement_of_purpose: additionalInfo.statement_of_purpose,
        special_needs: additionalInfo.special_needs,
        disability_declaration: additionalInfo.disability_declaration,
      }

      await axios.post(
        `/api/v1/apply/${schoolCode}/application/submit`,
        payload,
        { headers: { Authorization: `Bearer ${token}` } }
      )

      setSuccessMsg("Application submitted successfully! Redirecting to supporting documents...")
      setTimeout(() => {
        navigate(`/apply/${schoolCode}/documents`)
      }, 2000)
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "Failed to submit application. Please verify all required fields."
      )
    } finally {
      setLoading(false)
    }
  }

  if (fetching) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600 font-medium">Loading application form...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-blue-600 bg-blue-50 px-3 py-1 rounded-full">
              Official Application Form
            </span>
            <h1 className="text-2xl font-bold text-gray-900 mt-2">
              University Admission Application ({schoolCode?.toUpperCase()})
            </h1>
            <p className="text-sm text-gray-600 mt-1">
              Complete all sections accurately before submitting your application.
            </p>
          </div>
          <Button
            onClick={() => navigate(`/apply/${schoolCode}/dashboard`)}
            variant="outline"
            className="self-start md:self-auto"
          >
            ← Back to Dashboard
          </Button>
        </div>

        {/* Status Alerts */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg mb-6 text-sm">
            {error}
          </div>
        )}
        {successMsg && (
          <div className="bg-green-50 border border-green-200 text-green-700 p-4 rounded-lg mb-6 text-sm font-medium">
            {successMsg}
          </div>
        )}

        {/* Tab Navigation */}
        <div className="flex border-b border-gray-200 mb-8 overflow-x-auto bg-white rounded-t-xl shadow-sm p-2 gap-2">
          <button
            type="button"
            onClick={() => setActiveTab("personal")}
            className={`flex-1 py-3 px-4 text-sm font-medium rounded-lg text-center transition-colors whitespace-nowrap ${
              activeTab === "personal"
                ? "bg-blue-600 text-white shadow-sm"
                : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
            }`}
          >
            1. Personal Info
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("academic")}
            className={`flex-1 py-3 px-4 text-sm font-medium rounded-lg text-center transition-colors whitespace-nowrap ${
              activeTab === "academic"
                ? "bg-blue-600 text-white shadow-sm"
                : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
            }`}
          >
            2. WASSCE Results
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("programmes")}
            className={`flex-1 py-3 px-4 text-sm font-medium rounded-lg text-center transition-colors whitespace-nowrap ${
              activeTab === "programmes"
                ? "bg-blue-600 text-white shadow-sm"
                : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
            }`}
          >
            3. Programme Choices
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("statement")}
            className={`flex-1 py-3 px-4 text-sm font-medium rounded-lg text-center transition-colors whitespace-nowrap ${
              activeTab === "statement"
                ? "bg-blue-600 text-white shadow-sm"
                : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
            }`}
          >
            4. Statement & Submit
          </button>
        </div>

        {/* Form Container */}
        <form onSubmit={handleSubmitApplication} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 sm:p-8 space-y-6">
          {/* TAB 1: PERSONAL INFO */}
          {activeTab === "personal" && (
            <div className="space-y-6">
              <h2 className="text-xl font-bold text-gray-900 border-b pb-3">Personal & Contact Details</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">First Name *</label>
                  <Input
                    type="text"
                    value={personalInfo.first_name}
                    onChange={(e) => setPersonalInfo({ ...personalInfo, first_name: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Last Name *</label>
                  <Input
                    type="text"
                    value={personalInfo.last_name}
                    onChange={(e) => setPersonalInfo({ ...personalInfo, last_name: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Phone Number *</label>
                  <Input
                    type="tel"
                    value={personalInfo.phone}
                    onChange={(e) => setPersonalInfo({ ...personalInfo, phone: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Date of Birth</label>
                  <Input
                    type="date"
                    value={personalInfo.date_of_birth}
                    onChange={(e) => setPersonalInfo({ ...personalInfo, date_of_birth: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Gender</label>
                  <select
                    value={personalInfo.gender}
                    onChange={(e) => setPersonalInfo({ ...personalInfo, gender: e.target.value })}
                    className="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Nationality</label>
                  <Input
                    type="text"
                    value={personalInfo.nationality}
                    onChange={(e) => setPersonalInfo({ ...personalInfo, nationality: e.target.value })}
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Residential Address</label>
                  <Input
                    type="text"
                    placeholder="Street Address, P.O. Box"
                    value={personalInfo.address}
                    onChange={(e) => setPersonalInfo({ ...personalInfo, address: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">City / Town</label>
                  <Input
                    type="text"
                    value={personalInfo.city}
                    onChange={(e) => setPersonalInfo({ ...personalInfo, city: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Region</label>
                  <select
                    value={personalInfo.region}
                    onChange={(e) => setPersonalInfo({ ...personalInfo, region: e.target.value })}
                    className="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    <option value="Greater Accra">Greater Accra</option>
                    <option value="Ashanti">Ashanti</option>
                    <option value="Central">Central</option>
                    <option value="Eastern">Eastern</option>
                    <option value="Western">Western</option>
                    <option value="Volta">Volta</option>
                    <option value="Northern">Northern</option>
                    <option value="Upper East">Upper East</option>
                    <option value="Upper West">Upper West</option>
                    <option value="Bono">Bono</option>
                  </select>
                </div>
              </div>

              <div className="flex justify-end pt-4">
                <Button 
                  type="button" 
                  onClick={async () => {
                    try {
                      const token = localStorage.getItem("access_token")
                      if (token) {
                        await axios.put(
                          `/api/v1/apply/${schoolCode}/personal`,
                          personalInfo,
                          { headers: { Authorization: `Bearer ${token}` } }
                        )
                      }
                    } catch (e) {
                      console.error("Auto-save personal info error:", e)
                    }
                    setActiveTab("academic")
                  }} 
                  className="bg-blue-600 hover:bg-blue-700 text-white"
                >
                  Next: WASSCE Results →
                </Button>
              </div>
            </div>
          )}

          {/* TAB 2: WASSCE RESULTS */}
          {activeTab === "academic" && (
            <div className="space-y-6">
              <div className="flex justify-between items-center border-b pb-3">
                <h2 className="text-xl font-bold text-gray-900">WASSCE Academic Results</h2>
                <div className="bg-blue-50 border border-blue-200 px-3 py-1.5 rounded-lg text-xs font-semibold text-blue-800">
                  Computed Aggregate: <span className="text-sm font-bold text-blue-900">{calculateAggregate()}</span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">WASSCE Exam Year *</label>
                  <Input
                    type="number"
                    value={academicInfo.wassce_year}
                    onChange={(e) => setAcademicInfo({ ...academicInfo, wassce_year: Number(e.target.value) })}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Index Number *</label>
                  <Input
                    type="text"
                    placeholder="1012345678"
                    value={academicInfo.wassce_index_number}
                    onChange={(e) => setAcademicInfo({ ...academicInfo, wassce_index_number: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Examination Center</label>
                  <Input
                    type="text"
                    placeholder="Center Name / School Code"
                    value={academicInfo.wassce_center}
                    onChange={(e) => setAcademicInfo({ ...academicInfo, wassce_center: e.target.value })}
                  />
                </div>
              </div>

              <div className="pt-4">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-md font-bold text-gray-800">Subjects & Grades (Minimum 4, Max 10)</h3>
                  <Button type="button" onClick={handleAddSubject} variant="outline" size="sm">
                    + Add Subject
                  </Button>
                </div>

                <div className="space-y-3">
                  {academicInfo.subjects.map((item, idx) => (
                    <div key={idx} className="flex items-center gap-3 bg-gray-50 p-3 rounded-lg border border-gray-200">
                      <span className="text-sm font-bold text-gray-500 w-6">{idx + 1}.</span>
                      <select
                        value={item.subject}
                        onChange={(e) => handleSubjectChange(idx, "subject", e.target.value)}
                        className="flex-1 border border-gray-300 rounded-md p-2 text-sm bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                      >
                        {WASSCE_SUBJECTS.map((sub) => (
                          <option key={sub} value={sub}>
                            {sub}
                          </option>
                        ))}
                      </select>
                      <select
                        value={item.grade}
                        onChange={(e) => handleSubjectChange(idx, "grade", e.target.value)}
                        className="w-24 border border-gray-300 rounded-md p-2 text-sm bg-white font-semibold text-blue-700 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                      >
                        {Object.keys(GRADE_VALUES).map((grd) => (
                          <option key={grd} value={grd}>
                            {grd} ({GRADE_VALUES[grd]})
                          </option>
                        ))}
                      </select>
                      {academicInfo.subjects.length > 4 && (
                        <button
                          type="button"
                          onClick={() => handleRemoveSubject(idx)}
                          className="text-red-500 hover:text-red-700 px-2 py-1 text-lg font-bold"
                        >
                          ✕
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex justify-between pt-6 border-t">
                <Button type="button" onClick={() => setActiveTab("personal")} variant="outline">
                  ← Back to Personal Info
                </Button>
                <Button type="button" onClick={() => setActiveTab("programmes")} className="bg-blue-600 hover:bg-blue-700 text-white">
                  Next: Programme Choices →
                </Button>
              </div>
            </div>
          )}

          {/* TAB 3: PROGRAMME CHOICES */}
          {activeTab === "programmes" && (
            <div className="space-y-6">
              <h2 className="text-xl font-bold text-gray-900 border-b pb-3">Programme Selections</h2>
              <p className="text-sm text-gray-600">
                Select your preferred programmes of study in order of preference.
              </p>

              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">First Choice Programme *</label>
                  <select
                    value={programmeChoices.choice_1}
                    onChange={(e) => setProgrammeChoices({ ...programmeChoices, choice_1: e.target.value })}
                    className="w-full border border-gray-300 rounded-md p-2.5 text-sm bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    required
                  >
                    <option value="">Select First Choice</option>
                    {programmes.map((p) => (
                      <option key={p.id} value={p.code}>
                        {p.code} - {p.name} ({p.duration_years} Years)
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Second Choice Programme</label>
                  <select
                    value={programmeChoices.choice_2}
                    onChange={(e) => setProgrammeChoices({ ...programmeChoices, choice_2: e.target.value })}
                    className="w-full border border-gray-300 rounded-md p-2.5 text-sm bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    <option value="">Select Second Choice (Optional)</option>
                    {programmes.map((p) => (
                      <option key={p.id} value={p.code}>
                        {p.code} - {p.name} ({p.duration_years} Years)
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Third Choice Programme</label>
                  <select
                    value={programmeChoices.choice_3}
                    onChange={(e) => setProgrammeChoices({ ...programmeChoices, choice_3: e.target.value })}
                    className="w-full border border-gray-300 rounded-md p-2.5 text-sm bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    <option value="">Select Third Choice (Optional)</option>
                    {programmes.map((p) => (
                      <option key={p.id} value={p.code}>
                        {p.code} - {p.name} ({p.duration_years} Years)
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="flex justify-between pt-6 border-t">
                <Button type="button" onClick={() => setActiveTab("academic")} variant="outline">
                  ← Back to WASSCE Results
                </Button>
                <Button type="button" onClick={() => setActiveTab("statement")} className="bg-blue-600 hover:bg-blue-700 text-white">
                  Next: Statement & Submit →
                </Button>
              </div>
            </div>
          )}

          {/* TAB 4: STATEMENT & SUBMIT */}
          {activeTab === "statement" && (
            <div className="space-y-6">
              <h2 className="text-xl font-bold text-gray-900 border-b pb-3">Statement & Final Submission</h2>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Statement of Purpose / Motivation (Optional)
                </label>
                <textarea
                  rows={4}
                  placeholder="Explain why you wish to study your chosen programme at this university..."
                  value={additionalInfo.statement_of_purpose}
                  onChange={(e) => setAdditionalInfo({ ...additionalInfo, statement_of_purpose: e.target.value })}
                  className="w-full border border-gray-300 rounded-md p-3 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Disability / Special Needs Declaration</label>
                <Input
                  type="text"
                  placeholder="Indicate any special accessibility or medical requirements if applicable"
                  value={additionalInfo.special_needs}
                  onChange={(e) => setAdditionalInfo({ ...additionalInfo, special_needs: e.target.value })}
                />
              </div>

              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200 text-xs text-blue-800 space-y-2">
                <p className="font-bold">Applicant Declaration:</p>
                <p>
                  I hereby declare that all information provided in this application form is complete and accurate to the best of my knowledge.
                </p>
              </div>

              <div className="flex justify-between pt-6 border-t">
                <Button type="button" onClick={() => setActiveTab("programmes")} variant="outline">
                  ← Back to Programmes
                </Button>
                <Button
                  type="submit"
                  disabled={loading}
                  className="bg-green-600 hover:bg-green-700 text-white px-8 py-2.5 text-base font-bold shadow-md"
                >
                  {loading ? "Submitting Application..." : "Submit Application"}
                </Button>
              </div>
            </div>
          )}
        </form>
      </div>
    </div>
  )
}
