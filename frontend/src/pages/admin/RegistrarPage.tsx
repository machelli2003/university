import React, { useState } from "react"
import { AppShell } from "@/components/layout/AppShell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { documentApi } from "@/services/api/document"
import { getErrorMessage } from "@/services/api/client"
import type { DocumentSearchResult } from "@/types/document"

export default function RegistrarPage() {
  const [documentType, setDocumentType] = useState<string>("")
  const [uploadedBy, setUploadedBy] = useState<string>("")
  const [signedOnly, setSignedOnly] = useState<boolean>(false)
  const [searchResults, setSearchResults] = useState<DocumentSearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  async function handleSearch() {
    setError(null)
    setSuccess(null)
    setLoading(true)
    try {
      const results = await documentApi.searchDocuments({
        document_type: documentType || undefined,
        uploaded_by: uploadedBy || undefined,
        signed: signedOnly ? true : undefined,
      })
      setSearchResults(results)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  async function handleSign(documentId: string) {
    setError(null)
    setSuccess(null)
    setLoading(true)
    try {
      const result = await documentApi.signDocument(documentId)
      setSuccess(`Document signed: ${result.document_id}`)
      await handleSearch()
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-semibold text-ink mb-1">Registrar Dashboard</h1>
      <p className="text-cocoa-400 mb-6">Manage registration, student records, academic approvals, and official document workflows.</p>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 mb-6">
        <Card>
          <CardHeader>
            <CardTitle>Admissions Workflow</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-cocoa-500">Review applications, track admission progress, and approve student enrolments.</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Program Registration</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-cocoa-500">Manage programme registrations, course allocations, and degree planning for students.</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Transcript Oversight</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-cocoa-500">Monitor academic records, approve grade submissions, and keep student history accurate.</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Document Search & Signing</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
              <input
                value={documentType}
                onChange={(e) => setDocumentType(e.target.value)}
                placeholder="Document type"
                className="input w-full"
              />
              <input
                value={uploadedBy}
                onChange={(e) => setUploadedBy(e.target.value)}
                placeholder="Uploaded by user id"
                className="input w-full"
              />
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={signedOnly}
                  onChange={(e) => setSignedOnly(e.target.checked)}
                />
                <span className="text-sm text-cocoa-500">Signed only</span>
              </label>
              <button className="btn btn-primary w-full" onClick={handleSearch} disabled={loading}>
                {loading ? "Searching..." : "Search documents"}
              </button>
            </div>

            {error && <p className="text-sm text-red-500">{error}</p>}
            {success && <p className="text-sm text-emerald-600">{success}</p>}

            <div className="overflow-x-auto">
              <table className="w-full table-auto">
                <thead>
                  <tr>
                    <th className="text-left px-2 py-2">Name</th>
                    <th className="text-left px-2 py-2">Type</th>
                    <th className="text-left px-2 py-2">Uploaded By</th>
                    <th className="text-left px-2 py-2">Signed</th>
                    <th className="text-left px-2 py-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {searchResults.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="px-2 py-4 text-sm text-cocoa-500">No documents found.</td>
                    </tr>
                  ) : (
                    searchResults.map((doc) => (
                      <tr key={doc.id}>
                        <td className="px-2 py-2">{doc.document_name}</td>
                        <td className="px-2 py-2 capitalize">{doc.document_type.replace(/_/g, " ")}</td>
                        <td className="px-2 py-2">{doc.uploaded_by}</td>
                        <td className="px-2 py-2">{doc.is_signed ? "Yes" : "No"}</td>
                        <td className="px-2 py-2">
                          {!doc.is_signed ? (
                            <button className="btn btn-sm btn-secondary" onClick={() => handleSign(doc.id)} disabled={loading}>
                              Sign
                            </button>
                          ) : (
                            <span className="text-sm text-cocoa-500">Signed</span>
                          )}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </CardContent>
      </Card>
    </AppShell>
  )
}
