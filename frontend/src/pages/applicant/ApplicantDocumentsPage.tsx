/**
 * Applicant Portal Supporting Documents Page
 * Route: /apply/:schoolCode/documents
 *
 * Allows applicants to upload and manage supporting attachments:
 * - WASSCE Result Slip (Required)
 * - Birth Certificate / Ghana Card (Required)
 * - Passport Photo (Required)
 * - Transcripts / Testimonials (Optional)
 */

import React, { useState, useEffect } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { Button } from "@/components/ui/Button"
import axios from "axios"

interface UploadedDocument {
  id: string
  type: string
  name: string
  url: string
  uploaded_at: string
  status: "pending_review" | "approved" | "rejected"
}

const REQUIRED_DOCUMENTS = [
  { type: "wassce_result_slip", name: "WASSCE Result Slip", required: true, description: "Official WAEC result statement or printout" },
  { type: "birth_certificate", name: "Birth Certificate / Ghana Card", required: true, description: "Proof of age and legal identity" },
  { type: "passport_photo", name: "Passport Picture", required: true, description: "Recent passport-sized photograph with white background" },
  { type: "academic_transcript", name: "Academic Transcript / Testimonial", required: false, description: "Secondary school terminal reports or testimonial" },
  { type: "recommendation_letter", name: "Recommendation Letter", required: false, description: "Letter from school headmaster or referee" },
]

export default function ApplicantDocumentsPage() {
  const { schoolCode } = useParams<{ schoolCode: string }>()
  const navigate = useNavigate()

  const [documents, setDocuments] = useState<UploadedDocument[]>([])
  const [loading, setLoading] = useState(true)
  const [uploadingType, setUploadingType] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [successMsg, setSuccessMsg] = useState<string | null>(null)

  // Selected file for upload
  const [selectedFiles, setSelectedFiles] = useState<Record<string, File | null>>({})

  useEffect(() => {
    fetchDocuments()
  }, [schoolCode])

  const fetchDocuments = async () => {
    try {
      const token = localStorage.getItem("access_token")
      if (!token) {
        navigate(`/apply/${schoolCode}/login`)
        return
      }

      const response = await axios.get(`/api/v1/apply/${schoolCode}/documents`, {
        headers: { Authorization: `Bearer ${token}` },
      })

      if (response.data && Array.isArray(response.data.documents)) {
        setDocuments(response.data.documents)
      }
    } catch (err: any) {
      console.error("Error fetching documents:", err)
    } finally {
      setLoading(false)
    }
  }

  const handleFileSelect = (docType: string, e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFiles((prev) => ({ ...prev, [docType]: e.target.files![0] }))
    }
  }

  const handleUpload = async (docType: string) => {
    const file = selectedFiles[docType]
    if (!file) return

    setUploadingType(docType)
    setError(null)
    setSuccessMsg(null)

    try {
      const token = localStorage.getItem("access_token")
      const formData = new FormData()
      formData.append("file", file)
      formData.append("document_type", docType)
      formData.append("document_name", file.name)

      await axios.post(
        `/api/v1/apply/${schoolCode}/documents/upload`,
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "multipart/form-data",
          },
        }
      )

      // Add to local state
      const newDoc: UploadedDocument = {
        id: `doc_${Date.now()}`,
        type: docType,
        name: file.name,
        url: "#",
        uploaded_at: new Date().toISOString(),
        status: "pending_review",
      }

      setDocuments((prev) => [...prev.filter((d) => d.type !== docType), newDoc])
      setSelectedFiles((prev) => ({ ...prev, [docType]: null }))
      setSuccessMsg(`Document '${file.name}' uploaded successfully!`)
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "Upload failed. Please try again with a PDF or image file."
      )
    } finally {
      setUploadingType(null)
    }
  }

  const handleDelete = async (docId: string, docType: string) => {
    try {
      const token = localStorage.getItem("access_token")
      await axios.delete(`/api/v1/apply/${schoolCode}/documents/${docId}`, {
        headers: { Authorization: `Bearer ${token}` },
      })

      setDocuments((prev) => prev.filter((d) => d.id !== docId && d.type !== docType))
      setSuccessMsg("Document removed.")
    } catch {
      // Remove locally if mock
      setDocuments((prev) => prev.filter((d) => d.id !== docId && d.type !== docType))
    }
  }

  // Compute stats
  const uploadedTypes = new Set(documents.map((d) => d.type))
  const requiredCount = REQUIRED_DOCUMENTS.filter((d) => d.required).length
  const uploadedRequiredCount = REQUIRED_DOCUMENTS.filter((d) => d.required && uploadedTypes.has(d.type)).length
  const isComplete = uploadedRequiredCount >= requiredCount

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600 font-medium">Loading documents portal...</p>
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
              Supporting Attachments
            </span>
            <h1 className="text-2xl font-bold text-gray-900 mt-2">
              Application Supporting Documents ({schoolCode?.toUpperCase()})
            </h1>
            <p className="text-sm text-gray-600 mt-1">
              Upload clear PDF or Image copies of your credentials.
            </p>
          </div>
          <Button
            onClick={() => navigate(`/apply/${schoolCode}/dashboard`)}
            variant="outline"
          >
            ← Back to Dashboard
          </Button>
        </div>

        {/* Status Messages */}
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

        {/* Progress Bar */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-semibold text-gray-700">Required Documents Progress</span>
            <span className="text-sm font-bold text-blue-600">
              {uploadedRequiredCount} of {requiredCount} Required Uploaded
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className={`h-3 rounded-full transition-all duration-500 ${
                isComplete ? "bg-green-500" : "bg-blue-600"
              }`}
              style={{ width: `${(uploadedRequiredCount / requiredCount) * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Document Checklist Cards */}
        <div className="space-y-4">
          {REQUIRED_DOCUMENTS.map((docDef) => {
            const uploadedDoc = documents.find((d) => d.type === docDef.type)
            const isUploaded = Boolean(uploadedDoc)
            const isUploading = uploadingType === docDef.type

            return (
              <div
                key={docDef.type}
                className={`bg-white rounded-xl border p-6 shadow-sm transition-all ${
                  isUploaded ? "border-green-200 bg-green-50/20" : "border-gray-200"
                }`}
              >
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="text-lg font-bold text-gray-900">{docDef.name}</h3>
                      {docDef.required ? (
                        <span className="text-xs bg-red-100 text-red-700 font-semibold px-2 py-0.5 rounded">
                          Required
                        </span>
                      ) : (
                        <span className="text-xs bg-gray-100 text-gray-600 font-semibold px-2 py-0.5 rounded">
                          Optional
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-gray-500 mt-1">{docDef.description}</p>
                  </div>

                  {/* Status & Actions */}
                  <div className="flex items-center gap-3">
                    {isUploaded ? (
                      <div className="flex items-center gap-3">
                        <span className="inline-flex items-center gap-1.5 bg-green-100 text-green-800 text-xs font-semibold px-3 py-1.5 rounded-full">
                          ✓ Uploaded ({uploadedDoc?.name})
                        </span>
                        <Button
                          type="button"
                          onClick={() => handleDelete(uploadedDoc!.id, docDef.type)}
                          variant="outline"
                          size="sm"
                          className="text-red-600 hover:text-red-700 hover:bg-red-50 border-red-200"
                        >
                          Remove
                        </Button>
                      </div>
                    ) : (
                      <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
                        <input
                          type="file"
                          accept=".pdf,.png,.jpg,.jpeg"
                          id={`file-${docDef.type}`}
                          onChange={(e) => handleFileSelect(docDef.type, e)}
                          className="hidden"
                        />
                        <label
                          htmlFor={`file-${docDef.type}`}
                          className="cursor-pointer text-xs font-semibold bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-2 rounded-md border border-gray-300 text-center truncate max-w-[180px]"
                        >
                          {selectedFiles[docDef.type]
                            ? selectedFiles[docDef.type]!.name
                            : "Choose File (PDF/Image)"}
                        </label>
                        <Button
                          type="button"
                          disabled={!selectedFiles[docDef.type] || isUploading}
                          onClick={() => handleUpload(docDef.type)}
                          size="sm"
                          className="bg-blue-600 hover:bg-blue-700 text-white"
                        >
                          {isUploading ? "Uploading..." : "Upload"}
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>

        {/* Footer Actions */}
        <div className="mt-8 flex flex-col sm:flex-row justify-between items-center gap-4 bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
          <div>
            <p className="text-sm font-semibold text-gray-800">
              {isComplete ? "All required documents uploaded!" : "Please upload all required documents."}
            </p>
            <p className="text-xs text-gray-500">
              Supported file formats: PDF, PNG, JPG (Max 5MB per file)
            </p>
          </div>
          <Button
            onClick={() => navigate(`/apply/${schoolCode}/dashboard`)}
            className="w-full sm:w-auto bg-green-600 hover:bg-green-700 text-white font-bold px-6 py-2.5"
          >
            Return to Dashboard →
          </Button>
        </div>
      </div>
    </div>
  )
}
