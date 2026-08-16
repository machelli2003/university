import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { AppShell } from "@/components/layout/AppShell"
import { onboardingApi, type CreateUniversityApplicationRequest } from "@/services/api/onboarding"
import { getErrorMessage } from "@/services/api/client"

export default function UniversityApplicationFormPage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [submitted, setSubmitted] = useState(false)

  const [form, setForm] = useState<CreateUniversityApplicationRequest>({
    legal_name: "",
    display_name: "",
    school_code: "",
    admin_first_name: "",
    admin_last_name: "",
    admin_email: "",
    institution_type: "university",
    is_public: true,
    location: "",
    region: "Greater Accra",
    country: "Ghana",
    postal_address: "",
    official_email: "",
    official_phone: "",
    website: "",
    description: "",
    timezone: "Africa/Accra",
    currency: "GHS",
  })

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      const result = await onboardingApi.createApplication(form)
      setSubmitted(true)
      setTimeout(() => {
        navigate(`/admin/university-applications/${result.university_application_id}`)
      }, 1500)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <AppShell>
      <div className="max-w-4xl mx-auto space-y-6">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink mb-1">New University Application</h1>
          <p className="text-cocoa-400 mb-6">Fill in your university details to start the onboarding process.</p>
        </div>

        {submitted && <div className="rounded border border-green-200 bg-green-50 px-4 py-3 text-green-700">Application created successfully! Redirecting...</div>}
        {error && <div className="rounded border border-red-200 bg-red-50 px-4 py-3 text-red-700">{error}</div>}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* SECTION 1: SCHOOL IDENTITY */}
          <fieldset className="space-y-4 rounded-lg border border-cocoa-100 p-6 bg-white">
            <legend className="text-lg font-semibold text-ink">School Identity</legend>

            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-ink mb-1">Legal Name *</label>
                <input
                  className="w-full input"
                  type="text"
                  required
                  value={form.legal_name}
                  onChange={(e) => setForm({ ...form, legal_name: e.target.value })}
                  placeholder="Kwame Nkrumah University of Science and Technology"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-ink mb-1">Display Name</label>
                <input
                  className="w-full input"
                  type="text"
                  value={form.display_name}
                  onChange={(e) => setForm({ ...form, display_name: e.target.value })}
                  placeholder="KNUST"
                />
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-ink mb-1">School Code *</label>
                <input
                  className="w-full input"
                  type="text"
                  required
                  value={form.school_code}
                  onChange={(e) => setForm({ ...form, school_code: e.target.value.toUpperCase() })}
                  placeholder="KNUST"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-ink mb-1">Institution Type</label>
                <select
                  className="w-full input"
                  value={form.institution_type}
                  onChange={(e) => setForm({ ...form, institution_type: e.target.value })}
                >
                  <option value="university">University</option>
                  <option value="polytechnic">Polytechnic</option>
                  <option value="college">College</option>
                  <option value="secondary">Secondary School</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-ink mb-1">Description</label>
              <textarea
                className="w-full input min-h-[100px]"
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                placeholder="Brief description of your institution..."
              />
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="is_public"
                checked={form.is_public}
                onChange={(e) => setForm({ ...form, is_public: e.target.checked })}
                className="h-4 w-4"
              />
              <label htmlFor="is_public" className="text-sm font-medium text-ink">Public Institution</label>
            </div>
          </fieldset>

          {/* SECTION 2: ADMIN CONTACT */}
          <fieldset className="space-y-4 rounded-lg border border-cocoa-100 p-6 bg-white">
            <legend className="text-lg font-semibold text-ink">Administrator Contact</legend>

            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-ink mb-1">First Name *</label>
                <input
                  className="w-full input"
                  type="text"
                  required
                  value={form.admin_first_name}
                  onChange={(e) => setForm({ ...form, admin_first_name: e.target.value })}
                  placeholder="John"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-ink mb-1">Last Name *</label>
                <input
                  className="w-full input"
                  type="text"
                  required
                  value={form.admin_last_name}
                  onChange={(e) => setForm({ ...form, admin_last_name: e.target.value })}
                  placeholder="Doe"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-ink mb-1">Admin Email *</label>
              <input
                className="w-full input"
                type="email"
                required
                value={form.admin_email}
                onChange={(e) => setForm({ ...form, admin_email: e.target.value })}
                placeholder="admin@knust.edu.gh"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-ink mb-1">Official Email</label>
              <input
                className="w-full input"
                type="email"
                value={form.official_email}
                onChange={(e) => setForm({ ...form, official_email: e.target.value })}
                placeholder="registrar@knust.edu.gh"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-ink mb-1">Official Phone</label>
              <input
                className="w-full input"
                type="tel"
                value={form.official_phone}
                onChange={(e) => setForm({ ...form, official_phone: e.target.value })}
                placeholder="+233 XXXXXXXXX"
              />
            </div>
          </fieldset>

          {/* SECTION 3: LOCATION & SETTINGS */}
          <fieldset className="space-y-4 rounded-lg border border-cocoa-100 p-6 bg-white">
            <legend className="text-lg font-semibold text-ink">Location & Settings</legend>

            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-ink mb-1">Location</label>
                <input
                  className="w-full input"
                  type="text"
                  value={form.location}
                  onChange={(e) => setForm({ ...form, location: e.target.value })}
                  placeholder="Kumasi"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-ink mb-1">Region</label>
                <input
                  className="w-full input"
                  type="text"
                  value={form.region}
                  onChange={(e) => setForm({ ...form, region: e.target.value })}
                  placeholder="Ashanti"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-ink mb-1">Postal Address</label>
              <input
                className="w-full input"
                type="text"
                value={form.postal_address}
                onChange={(e) => setForm({ ...form, postal_address: e.target.value })}
                placeholder="P.O. Box 1234, Kumasi"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-ink mb-1">Website</label>
              <input
                className="w-full input"
                type="url"
                value={form.website}
                onChange={(e) => setForm({ ...form, website: e.target.value })}
                placeholder="https://knust.edu.gh"
              />
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-ink mb-1">Timezone</label>
                <select
                  className="w-full input"
                  value={form.timezone}
                  onChange={(e) => setForm({ ...form, timezone: e.target.value })}
                >
                  <option value="Africa/Accra">Africa/Accra (GMT)</option>
                  <option value="Africa/Lagos">Africa/Lagos (WAT)</option>
                  <option value="Africa/Johannesburg">Africa/Johannesburg (SAST)</option>
                  <option value="UTC">UTC</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-ink mb-1">Currency</label>
                <select
                  className="w-full input"
                  value={form.currency}
                  onChange={(e) => setForm({ ...form, currency: e.target.value })}
                >
                  <option value="GHS">GHS (Ghana Cedis)</option>
                  <option value="USD">USD (US Dollar)</option>
                  <option value="EUR">EUR (Euro)</option>
                </select>
              </div>
            </div>
          </fieldset>

          {/* SUBMIT BUTTON */}
          <div className="flex gap-3">
            <button type="submit" disabled={loading} className="btn btn-primary">
              {loading ? "Creating..." : "Create Application"}
            </button>
            <button type="button" onClick={() => navigate("/dashboard")} className="btn btn-secondary">
              Cancel
            </button>
          </div>
        </form>
      </div>
    </AppShell>
  )
}
