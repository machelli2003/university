import { useState } from "react"
import { useForm } from "react-hook-form"
import { AppShell } from "@/components/layout/AppShell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Select } from "@/components/ui/Select"
import { ErrorAlert, SuccessAlert, Spinner } from "@/components/ui/Feedback"
import { useUploadDocument, useMyDocuments, useVerifyDocument } from "@/hooks/useDocument"
import { getErrorMessage } from "@/services/api/client"
import type { CreateDocumentRequest } from "@/types/document"

const DOC_TYPES = ["admission_letter", "transcript", "certificate", "student_id", "other"]

export default function DocumentsPage() {
  const uploadMutation = useUploadDocument()
  const { data: documents, isLoading } = useMyDocuments()
  const [verifyId, setVerifyId] = useState<string | null>(null)
  const verifyQuery = useVerifyDocument(verifyId)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const { register, handleSubmit, reset } = useForm<CreateDocumentRequest>({
    defaultValues: { document_name: "", document_type: "other" },
  })

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-semibold text-ink mb-1">Documents</h1>
      <p className="text-cocoa-400 mb-6">Upload official documents and verify them via QR code.</p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader><CardTitle>Upload Document</CardTitle></CardHeader>
          <CardContent>
            {uploadMutation.isError && <ErrorAlert message={getErrorMessage(uploadMutation.error)} />}
            {uploadMutation.isSuccess && (
              <div className="mb-4">
                <SuccessAlert message="Document uploaded with QR verification code." />
                <img src={uploadMutation.data.qr_code} alt="QR Code" className="mt-3 h-32 w-32 border border-cocoa-100 rounded" />
              </div>
            )}

            <form
              onSubmit={handleSubmit((data: CreateDocumentRequest) => {
                if (!selectedFile) return
                uploadMutation.mutate(
                  { ...data, file: selectedFile },
                  {
                    onSuccess: () => {
                      reset()
                      setSelectedFile(null)
                    },
                  }
                )
              })}
              className="space-y-3"
            >
              <Input label="Document Name" {...register("document_name", { required: true })} />
              <Select label="Document Type" {...register("document_type")}>
                {DOC_TYPES.map((t) => (
                  <option key={t} value={t} className="capitalize">{t.replace(/_/g, " ")}</option>
                ))}
              </Select>
              <label className="block text-sm font-medium text-ink">
                File Upload
                <input
                  type="file"
                  className="mt-2 block w-full text-sm text-cocoa-700 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-cocoa-100 file:text-cocoa-700"
                  onChange={(event) => {
                    const file = event.target.files?.[0] ?? null
                    setSelectedFile(file)
                  }}
                />
              </label>
              <Button type="submit" isLoading={uploadMutation.isPending} disabled={!selectedFile}>
                Upload
              </Button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>My Documents</CardTitle></CardHeader>
          <CardContent>
            {isLoading && <Spinner />}
            <div className="space-y-2">
              {documents?.map((d) => (
                <div key={d.id} className="flex items-center justify-between border border-cocoa-100 rounded-md px-4 py-2">
                  <div>
                    <p className="text-sm font-medium">{d.document_name}</p>
                    <p className="text-xs text-cocoa-400 capitalize">{d.document_type.replace(/_/g, " ")}</p>
                  </div>
                  <Button size="sm" variant="outline" onClick={() => setVerifyId(d.id)}>Verify</Button>
                </div>
              ))}
              {documents && documents.length === 0 && (
                <p className="text-sm text-cocoa-400">No documents uploaded yet.</p>
              )}
            </div>

            {verifyQuery.data && (
              <div className="mt-4 border-t border-cocoa-100 pt-4">
                <SuccessAlert
                  message={`Verified: ${verifyQuery.data.document_name} — signed: ${verifyQuery.data.is_signed ? "yes" : "no"}`}
                />
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </AppShell>
  )
}
