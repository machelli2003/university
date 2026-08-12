import { useState } from "react"
import { useParams } from "react-router-dom"
import { AppShell } from "@/components/layout/AppShell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { useLecturerMaterials, useUploadMaterial } from "@/hooks/useLecturer"
import { Spinner, ErrorAlert, SuccessAlert } from "@/components/ui/Feedback"
import { getErrorMessage } from "@/services/api/client"

export default function CourseMaterialsPage() {
  const { courseId } = useParams()
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [materialType, setMaterialType] = useState("syllabus")
  const [file, setFile] = useState<File | null>(null)
  const [message, setMessage] = useState<string | null>(null)

  const { data, isLoading, error, refetch } = useLecturerMaterials(courseId || "")
  const uploadMutation = useUploadMaterial()

  async function handleUpload() {
    if (!courseId || !file) {
      setMessage("Please select a file to upload.")
      return
    }
    setMessage(null)
    const formData = new FormData()
    formData.append("title", title || file.name)
    formData.append("material_type", materialType)
    formData.append("description", description)
    formData.append("file", file)

    try {
      await uploadMutation.mutateAsync({ courseId, formData })
      setTitle("")
      setDescription("")
      setFile(null)
      setMessage("Material uploaded successfully.")
      refetch()
    } catch (err) {
      setMessage(getErrorMessage(err))
    }
  }

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink mb-1">Course Materials</h1>
          <p className="text-cocoa-400">Upload and manage syllabi, reading lists, and assignments for this course.</p>
        </div>

        <Card className="max-w-2xl">
          <CardHeader><CardTitle>Upload Material</CardTitle></CardHeader>
          <CardContent>
            {uploadMutation.isError && <ErrorAlert message={getErrorMessage(uploadMutation.error)} />}
            {message && <SuccessAlert message={message} />}
            <div className="space-y-4">
              <Input label="Title" value={title} onChange={(e) => setTitle(e.target.value)} />
              <label className="block">
                <span className="text-sm font-medium text-cocoa-600">Type</span>
                <select value={materialType} onChange={(e) => setMaterialType(e.target.value)} className="input w-full mt-1">
                  <option value="syllabus">Syllabus</option>
                  <option value="reading_list">Reading List</option>
                  <option value="assignment">Assignment</option>
                  <option value="other">Other</option>
                </select>
              </label>
              <label className="block">
                <span className="text-sm font-medium text-cocoa-600">Description</span>
                <textarea value={description} onChange={(e) => setDescription(e.target.value)} className="input w-full mt-1 h-24" />
              </label>
              <label className="block">
                <span className="text-sm font-medium text-cocoa-600">File</span>
                <input type="file" onChange={(e) => setFile(e.target.files?.[0] ?? null)} className="mt-2" />
              </label>
              <Button onClick={handleUpload} isLoading={uploadMutation.isPending}>Upload</Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Uploaded Materials</CardTitle></CardHeader>
          <CardContent>
            {isLoading && <div className="flex justify-center py-8"><Spinner className="h-8 w-8" /></div>}
            {error && <ErrorAlert message={getErrorMessage(error)} />}
            {!isLoading && !error && data?.length === 0 && (
              <p className="text-cocoa-400">No materials uploaded yet.</p>
            )}
            {!isLoading && data?.length > 0 && (
              <div className="space-y-4">
                {data.map((material: any) => (
                  <div key={material.id} className="border p-4 rounded">
                    <div className="font-semibold">{material.title}</div>
                    <div className="text-sm text-cocoa-500">{material.material_type.replace("_", " ")}</div>
                    <div className="text-sm text-cocoa-400">{material.description}</div>
                    <div className="mt-2">
                      <a href={material.file_url} target="_blank" rel="noreferrer" className="text-primary">Open file</a>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </AppShell>
  )
}
