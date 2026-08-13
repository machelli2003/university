import { useState, type FormEvent } from "react"
import { AppShell } from "@/components/layout/AppShell"
import { Button } from "@/components/ui/Button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Input } from "@/components/ui/Input"
import { Textarea } from "@/components/ui/Textarea"
import { ErrorAlert, Spinner, SuccessAlert } from "@/components/ui/Feedback"
import { useCreateUniversityApplication, useMyUniversityApplications } from "@/hooks/useOnboarding"
import type { CreateUniversityApplicationRequest } from "@/types/onboarding"

const defaultValues: CreateUniversityApplicationRequest = {
  legal_name: "",
  display_name: "",
  school_code: "",
  admin_first_name: "",
  admin_last_name: "",
  admin_email: "",
  institution_type: "",
  is_public: false,
  location: "",
  region: "",
  country: "",
  postal_address: "",
  official_email: "",
  official_phone: "",
  website: "",
  logo_url: "",
  favicon_url: "",
  description: "",
  academic_calendar_type: "",
  timezone: "",
  currency: "",
}

export default function UniversityApplicationsPage() {
  const [form, setForm] = useState<CreateUniversityApplicationRequest>(defaultValues)
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const applicationsQuery = useMyUniversityApplications()
  const createMutation = useCreateUniversityApplication()

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setMessage(null)
    setError(null)

    try {
      await createMutation.mutateAsync(form)
      setMessage("University application created successfully.")
      setForm(defaultValues)
      applicationsQuery.refetch()
    } catch (err) {
      setError((err as Error).message)
    }
  }

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink mb-1">University Onboarding</h1>
          <p className="text-cocoa-400">Create a new university application for onboarding and review pending tenant requests.</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Create New University Application</CardTitle>
          </CardHeader>
          <CardContent>
            {error && <ErrorAlert message={error} />}
            {message && <SuccessAlert message={message} />}

            <form className="space-y-4" onSubmit={handleSubmit}>
              <div className="grid gap-4 lg:grid-cols-2">
                <Input label="Legal name" value={form.legal_name} onChange={(e) => setForm({ ...form, legal_name: e.target.value })} required />
                <Input label="Display name" value={form.display_name} onChange={(e) => setForm({ ...form, display_name: e.target.value })} />
                <Input label="School code" value={form.school_code} onChange={(e) => setForm({ ...form, school_code: e.target.value })} required />
                <Input label="Admin first name" value={form.admin_first_name} onChange={(e) => setForm({ ...form, admin_first_name: e.target.value })} required />
                <Input label="Admin last name" value={form.admin_last_name} onChange={(e) => setForm({ ...form, admin_last_name: e.target.value })} required />
                <Input label="Admin email" type="email" value={form.admin_email} onChange={(e) => setForm({ ...form, admin_email: e.target.value })} required />
                <Input label="Official email" type="email" value={form.official_email} onChange={(e) => setForm({ ...form, official_email: e.target.value })} />
                <Input label="Official phone" value={form.official_phone} onChange={(e) => setForm({ ...form, official_phone: e.target.value })} />
                <Input label="Country" value={form.country} onChange={(e) => setForm({ ...form, country: e.target.value })} />
                <Input label="Timezone" value={form.timezone} onChange={(e) => setForm({ ...form, timezone: e.target.value })} />
                <Input label="Website" type="url" value={form.website} onChange={(e) => setForm({ ...form, website: e.target.value })} />
                <Input label="Logo URL" type="url" value={form.logo_url} onChange={(e) => setForm({ ...form, logo_url: e.target.value })} />
                <Input label="Favicon URL" type="url" value={form.favicon_url} onChange={(e) => setForm({ ...form, favicon_url: e.target.value })} />
                <Input label="Institution type" value={form.institution_type} onChange={(e) => setForm({ ...form, institution_type: e.target.value })} />
                <Input label="Postal address" value={form.postal_address} onChange={(e) => setForm({ ...form, postal_address: e.target.value })} />
              </div>
              <Textarea label="Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
              <Button type="submit" isLoading={createMutation.isPending}>Create application</Button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Pending Applications</CardTitle>
          </CardHeader>
          <CardContent>
            {applicationsQuery.isLoading && (
              <div className="flex justify-center py-8">
                <Spinner className="h-8 w-8" />
              </div>
            )}
            {applicationsQuery.isError && (
              <ErrorAlert message="Unable to load applications." />
            )}
            {applicationsQuery.data && applicationsQuery.data.length === 0 && !applicationsQuery.isLoading && (
              <p className="text-sm text-cocoa-500">No university applications found.</p>
            )}
            {applicationsQuery.data && applicationsQuery.data.length > 0 && (
              <div className="space-y-3">
                {applicationsQuery.data.map((application) => (
                  <div key={application.id} className="rounded-lg border border-cocoa-100 p-4">
                    <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                      <div>
                        <p className="font-semibold text-ink">{application.legal_name}</p>
                        <p className="text-xs text-cocoa-500">{application.school_code}</p>
                      </div>
                      <div className="text-sm text-cocoa-500">
                        {application.status.replace(/_/g, " ")}
                      </div>
                    </div>
                    <div className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2 text-sm text-cocoa-600">
                      <div>Requested by: {application.requested_by}</div>
                      <div>Tenant: {application.tenant_id ?? "Unassigned"}</div>
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
