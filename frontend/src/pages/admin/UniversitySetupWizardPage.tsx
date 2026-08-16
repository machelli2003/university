import { useEffect, useMemo, useState } from "react"
import { AppShell } from "@/components/layout/AppShell"
import { Button } from "@/components/ui/Button"
import { onboardingApi, type UniversityApplicationResponse } from "@/services/api/onboarding"
import { getErrorMessage } from "@/services/api/client"
import { useNavigate } from "react-router-dom"
import { AlertCircle, CheckCircle2, Clock } from "lucide-react"

const WIZARD_STEPS = [
  { key: "university_information", label: "University Information", icon: "🏛️", section: 1 },
  { key: "id_configuration", label: "ID Configuration", icon: "🆔", section: 2 },
  { key: "academic_years", label: "Academic Year", icon: "📅", section: 3 },
  { key: "faculties", label: "Faculties", icon: "🏢", section: 4 },
  { key: "departments", label: "Departments", icon: "📊", section: 5 },
  { key: "programmes", label: "Programmes", icon: "🎓", section: 6 },
  { key: "courses", label: "Courses", icon: "📚", section: 7 },
  { key: "admission_cycle", label: "Admission Cycle", icon: "📋", section: 8 },
  { key: "admission_requirements", label: "Admission Requirements", icon: "✅", section: 9 },
  { key: "application_form", label: "Application Form", icon: "📝", section: 10 },
  { key: "application_fee", label: "Application Fee", icon: "💰", section: 11 },
  { key: "staff", label: "Staff", icon: "👥", section: 12 },
  { key: "student_id_configuration", label: "Student ID Config", icon: "🎫", section: 13 },
  { key: "staff_id_configuration", label: "Staff ID Config", icon: "🎫", section: 14 },
  { key: "applicant_id_configuration", label: "Applicant ID Config", icon: "🎫", section: 15 },
  { key: "finance", label: "Finance", icon: "💳", section: 16 },
  { key: "grading", label: "Grading", icon: "📊", section: 17 },
  { key: "graduation", label: "Graduation", icon: "🎉", section: 18 },
  { key: "module_enablement", label: "Module Enablement", icon: "⚙️", section: 19 },
  { key: "admission_categories", label: "Admission Categories", icon: "📂", section: 20 },
  { key: "role_permission", label: "Role & Permissions", icon: "🔐", section: 21 },
  { key: "hostel", label: "Hostel Configuration", icon: "🏨", section: 22 },
  { key: "library", label: "Library Configuration", icon: "📖", section: 23 },
] as const

export default function UniversitySetupWizardPage() {
  const [application, setApplication] = useState<UniversityApplicationResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [activeStep, setActiveStep] = useState<string>(WIZARD_STEPS[0].key)
  const [formData, setFormData] = useState<Record<string, any>>({})
  const [submitting, setSubmitting] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    loadApplication()
  }, [])

  useEffect(() => {
    if (application) {
      setFormData(getInitialFormData(application, activeStep))
    }
  }, [activeStep, application])

  async function createInitialApplication() {
    setLoading(true)
    setError(null)
    try {
      const created = await onboardingApi.createApplication({
        legal_name: "University of Machelli",
        display_name: "UOM",
        school_code: "UOM",
        admin_first_name: "University",
        admin_last_name: "Admin",
        admin_email: "admin@university.edu"
      })
      setApplication(created)
      setError(null)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  async function loadApplication() {
    try {
      // Load applications for current user/tenant
      const applications = await onboardingApi.listApplications()
      
      if (!applications || applications.length === 0) {
        try {
          const created = await onboardingApi.createApplication({
            legal_name: "University of Machelli",
            display_name: "UOM",
            school_code: "UOM",
            admin_first_name: "University",
            admin_last_name: "Admin",
            admin_email: "admin@university.edu"
          })
          setApplication(created)
          setError(null)
          return
        } catch {
          setError("No university setup application found. Please click 'Initialize Setup Application' to start.")
          return
        }
      }

      // Use the first application (typically the active/current one)
      const data = applications[0]
      setApplication(data)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  const setupSections = useMemo(() => application?.setup_sections ?? {}, [application])
  const completedCount = Object.values(setupSections).filter(Boolean).length
  const completionPercent = Math.round((completedCount / WIZARD_STEPS.length) * 100)

  async function saveSection() {
    if (!application) {
      setError("Please initialize a university setup application first.")
      return
    }
    setSaving(true)
    setError(null)
    try {
      const updated = await onboardingApi.updateWizardSection(
        application.university_application_id,
        activeStep,
        formData
      )
      setApplication(updated)
      // Auto-advance to next incomplete section
      const nextIncomplete = WIZARD_STEPS.find((s) => !updated.setup_sections[s.key])
      if (nextIncomplete) setActiveStep(nextIncomplete.key)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setSaving(false)
    }
  }

  async function submitForReview() {
    if (completedCount < WIZARD_STEPS.length) {
      setError("All sections must be completed before submission")
      return
    }
    setSubmitting(true)
    setError(null)
    try {
      await onboardingApi.submitForReview(application?.university_application_id ?? "")
      navigate("/admin/university-applications")
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <AppShell>
        <div className="flex items-center justify-center h-96 text-cocoa-600">
          <Clock className="h-6 w-6 mr-2 animate-spin" />
          Loading university setup...
        </div>
      </AppShell>
    )
  }

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex items-center justify-between gap-4">
          <div>
            <h1 className="font-display text-3xl font-semibold text-ink">University Setup Wizard</h1>
            <p className="text-cocoa-500 mt-1">Configure your institution before going live</p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-cocoa-700">{completionPercent}%</div>
            <p className="text-sm text-cocoa-500">{completedCount} of {WIZARD_STEPS.length} sections</p>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="rounded-lg bg-white border border-cocoa-100 p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-ink">Overall Progress</span>
            <span className="text-xs text-cocoa-500">{completedCount}/{WIZARD_STEPS.length} complete</span>
          </div>
          <div className="w-full bg-cocoa-100 rounded-full h-2">
            <div 
              className="bg-green-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${completionPercent}%` }}
            />
          </div>
        </div>

        {error && (
          <div className="rounded border border-red-200 bg-red-50 px-4 py-3 flex items-center justify-between gap-3">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
              <span className="text-sm text-red-700">{error}</span>
            </div>
            {!application && (
              <Button onClick={createInitialApplication} variant="primary" size="sm">
                Initialize Setup Application
              </Button>
            )}
          </div>
        )}

        <div className="grid gap-6 lg:grid-cols-[280px_minmax(0,1fr)]">
          {/* Step List */}
          <aside className="rounded-lg border border-cocoa-100 bg-white p-4 h-fit">
            <h3 className="text-sm font-semibold text-ink mb-3">Setup Steps</h3>
            <div className="space-y-1">
              {WIZARD_STEPS.map((step) => {
                const isComplete = Boolean(setupSections[step.key])
                const isActive = step.key === activeStep
                return (
                  <button
                    key={step.key}
                    type="button"
                    onClick={() => setActiveStep(step.key)}
                    className={`flex w-full items-center gap-3 rounded-md px-3 py-2 text-left text-sm transition ${
                      isActive
                        ? "bg-cocoa-100 text-cocoa-800 font-medium"
                        : isComplete
                        ? "text-cocoa-600 hover:bg-green-50"
                        : "text-cocoa-500 hover:bg-cocoa-50"
                    }`}
                  >
                    <span>{step.icon}</span>
                    <span className="flex-1">{step.label}</span>
                    {isComplete && <CheckCircle2 className="h-4 w-4 text-green-500" />}
                  </button>
                )
              })}
            </div>
          </aside>

          {/* Step Content */}
          <div className="rounded-lg border border-cocoa-100 bg-white p-6 space-y-6">
            <div className="flex items-center justify-between border-b border-cocoa-100 pb-4">
              <div>
                <h2 className="text-2xl font-semibold text-ink">
                  {WIZARD_STEPS.find((s) => s.key === activeStep)?.label}
                </h2>
                <p className="text-sm text-cocoa-500 mt-1">
                  Step {WIZARD_STEPS.find((s) => s.key === activeStep)?.section} of {WIZARD_STEPS.length}
                </p>
              </div>
              <div className="flex gap-2">
                <Button onClick={saveSection} disabled={saving} variant="primary">
                  {saving ? "Saving..." : "Save Section"}
                </Button>
              </div>
            </div>

            {/* Dynamic Form Rendering */}
            <div className="grid gap-4 md:grid-cols-2">
              {renderFormFields(activeStep, formData, setFormData)}
            </div>
          </div>
        </div>

        {/* Submit Footer */}
        {completedCount === WIZARD_STEPS.length && (
          <div className="rounded-lg bg-green-50 border border-green-200 p-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-green-600" />
              <span className="text-sm text-green-700">All sections completed! Ready to submit for review.</span>
            </div>
            <Button onClick={submitForReview} disabled={submitting} variant="primary">
              {submitting ? "Submitting..." : "Submit for Super Admin Review"}
            </Button>
          </div>
        )}
      </div>
    </AppShell>
  )
}

function getInitialFormData(app: UniversityApplicationResponse | null, step: string): Record<string, any> {
  if (!app) return {}
  const keyMap: Record<string, string> = {
    university_information: "university_information",
    id_configuration: "id_configuration",
    academic_years: "academic_year_configuration",
    faculties: "faculties_configuration",
    departments: "departments_configuration",
    programmes: "programmes_configuration",
    courses: "courses_configuration",
    admission_cycle: "admission_cycle_configuration",
    admission_categories: "admission_categories_configuration",
    admission_requirements: "admission_requirements_configuration",
    application_form: "application_form_configuration",
    application_fee: "application_fee_configuration",
    staff: "staff_setup_configuration",
    student_id_configuration: "student_id_configuration",
    staff_id_configuration: "staff_id_configuration",
    applicant_id_configuration: "applicant_id_configuration",
    finance: "finance_configuration",
    grading: "grading_configuration",
    graduation: "graduation_configuration",
    module_enablement: "module_enablement",
    role_permission: "role_permission_configuration",
    hostel: "hostel_configuration",
    library: "library_configuration",
  }

  const propName = keyMap[step]
  let existing = propName ? (app as any)[propName] : null

  if (step === "university_information") {
    return {
      legal_name: app.legal_name || existing?.legal_name || "",
      display_name: app.display_name || existing?.display_name || "",
      school_code: app.school_code || existing?.school_code || "",
      country: app.country || existing?.country || "",
      timezone: app.timezone || existing?.timezone || "",
      official_email: app.official_email || existing?.official_email || "",
      ...(existing || {})
    }
  }

  return existing ? { ...existing } : {}
}

function renderFormFields(
  step: string,
  formData: Record<string, any>,
  setFormData: (data: Record<string, any>) => void
) {
  const updateField = (key: string, value: any) => {
    setFormData({ ...formData, [key]: value })
  }

  switch (step) {
    case "university_information":
      return (
        <>
          <FormField
            label="Legal Name"
            value={formData.legal_name || ""}
            onChange={(v) => updateField("legal_name", v)}
            placeholder="e.g., Kwame Nkrumah University of Science and Technology"
          />
          <FormField
            label="Display Name"
            value={formData.display_name || ""}
            onChange={(v) => updateField("display_name", v)}
            placeholder="e.g., KNUST"
          />
          <FormField
            label="School Code"
            value={formData.school_code || ""}
            onChange={(v) => updateField("school_code", v)}
            placeholder="e.g., KNUST"
          />
          <FormField
            label="Country"
            value={formData.country || ""}
            onChange={(v) => updateField("country", v)}
            placeholder="e.g., Ghana"
          />
          <FormField
            label="Timezone"
            value={formData.timezone || ""}
            onChange={(v) => updateField("timezone", v)}
            placeholder="e.g., Africa/Accra"
          />
          <FormField
            label="Official Email"
            type="email"
            value={formData.official_email || ""}
            onChange={(v) => updateField("official_email", v)}
            placeholder="admin@university.edu"
          />
        </>
      )

    case "id_configuration":
      return (
        <>
          <FormField
            label="Student ID Pattern"
            value={formData.student_id_pattern || ""}
            onChange={(v) => updateField("student_id_pattern", v)}
            placeholder="{SCHOOL_CODE}-{YEAR}-{SEQUENCE}"
            helperText="Use {SCHOOL_CODE}, {YEAR}, {SEQUENCE} as placeholders"
          />
          <FormField
            label="Staff ID Pattern"
            value={formData.staff_id_pattern || ""}
            onChange={(v) => updateField("staff_id_pattern", v)}
            placeholder="{SCHOOL_CODE}-STF-{SEQUENCE}"
          />
          <FormField
            label="Applicant ID Pattern"
            value={formData.applicant_id_pattern || ""}
            onChange={(v) => updateField("applicant_id_pattern", v)}
            placeholder="{SCHOOL_CODE}-APP-{YEAR}-{SEQUENCE}"
          />
          <FormField
            type="number"
            label="Starting Sequence"
            value={formData.starting_sequence || ""}
            onChange={(v) => updateField("starting_sequence", v)}
            placeholder="1"
          />
        </>
      )

    case "academic_years":
      return (
        <>
          <FormField
            label="Current Academic Year"
            value={formData.current_year || ""}
            onChange={(v) => updateField("current_year", v)}
            placeholder="e.g., 2026/2027"
          />
          <FormField
            label="Next Academic Year"
            value={formData.next_year || ""}
            onChange={(v) => updateField("next_year", v)}
            placeholder="e.g., 2027/2028"
          />
          <FormField
            type="date"
            label="Year Start Date"
            value={formData.year_start_date || ""}
            onChange={(v) => updateField("year_start_date", v)}
          />
          <FormField
            type="date"
            label="Year End Date"
            value={formData.year_end_date || ""}
            onChange={(v) => updateField("year_end_date", v)}
          />
        </>
      )

    case "faculties":
      return (
        <>
          <FormField
            label="Faculty Name"
            value={formData.faculty_name || ""}
            onChange={(v) => updateField("faculty_name", v)}
            placeholder="e.g., Faculty of Computing"
          />
          <FormField
            label="Faculty Code"
            value={formData.faculty_code || ""}
            onChange={(v) => updateField("faculty_code", v)}
            placeholder="e.g., FOC"
          />
          <FormField
            label="Dean Email"
            type="email"
            value={formData.dean_email || ""}
            onChange={(v) => updateField("dean_email", v)}
            placeholder="dean@university.edu"
          />
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-ink mb-1">Description</label>
            <textarea
              value={formData.description || ""}
              onChange={(e) => updateField("description", e.target.value)}
              placeholder="Faculty description and overview"
              className="w-full px-3 py-2 border border-cocoa-200 rounded-md text-sm focus:border-cocoa-400 focus:outline-none"
              rows={3}
            />
          </div>
        </>
      )

    case "departments":
      return (
        <>
          <FormField
            label="Department Name"
            value={formData.department_name || ""}
            onChange={(v) => updateField("department_name", v)}
            placeholder="e.g., Computer Science"
          />
          <FormField
            label="Department Code"
            value={formData.department_code || ""}
            onChange={(v) => updateField("department_code", v)}
            placeholder="e.g., CS"
          />
          <FormField
            label="Faculty"
            value={formData.faculty_id || ""}
            onChange={(v) => updateField("faculty_id", v)}
            placeholder="Select or enter faculty code"
          />
          <FormField
            label="HOD Email"
            type="email"
            value={formData.hod_email || ""}
            onChange={(v) => updateField("hod_email", v)}
            placeholder="hod@university.edu"
          />
        </>
      )

    case "programmes":
      return (
        <>
          <FormField
            label="Programme Name"
            value={formData.programme_name || ""}
            onChange={(v) => updateField("programme_name", v)}
            placeholder="e.g., BSc Computer Science"
          />
          <FormField
            label="Degree Type"
            value={formData.degree_type || ""}
            onChange={(v) => updateField("degree_type", v)}
            placeholder="e.g., BSc, MSc, HND"
          />
          <FormField
            type="number"
            label="Duration (Years)"
            value={formData.duration_years || ""}
            onChange={(v) => updateField("duration_years", v)}
            placeholder="4"
          />
          <FormField
            type="number"
            label="Intake Capacity"
            value={formData.capacity || ""}
            onChange={(v) => updateField("capacity", v)}
            placeholder="200"
          />
        </>
      )

    case "courses":
      return (
        <>
          <FormField
            label="Course Code"
            value={formData.course_code || ""}
            onChange={(v) => updateField("course_code", v)}
            placeholder="e.g., CSC101"
          />
          <FormField
            label="Course Title"
            value={formData.course_title || ""}
            onChange={(v) => updateField("course_title", v)}
            placeholder="e.g., Introduction to Computing"
          />
          <FormField
            type="number"
            label="Credit Hours"
            value={formData.credit_hours || ""}
            onChange={(v) => updateField("credit_hours", v)}
            placeholder="3"
          />
          <FormField
            label="Course Level"
            value={formData.level || ""}
            onChange={(v) => updateField("level", v)}
            placeholder="e.g., 100, 200, 300, 400"
          />
        </>
      )

    case "admission_cycle":
      return (
        <>
          <FormField
            label="Cycle Name"
            value={formData.cycle_name || ""}
            onChange={(v) => updateField("cycle_name", v)}
            placeholder="e.g., 2026 Entry"
          />
          <FormField
            label="Academic Year"
            value={formData.academic_year || ""}
            onChange={(v) => updateField("academic_year", v)}
            placeholder="e.g., 2026/2027"
          />
          <FormField
            type="date"
            label="Opening Date"
            value={formData.opening_date || ""}
            onChange={(v) => updateField("opening_date", v)}
          />
          <FormField
            type="time"
            label="Opening Time"
            value={formData.opening_time || ""}
            onChange={(v) => updateField("opening_time", v)}
          />
          <FormField
            type="date"
            label="Closing Date"
            value={formData.closing_date || ""}
            onChange={(v) => updateField("closing_date", v)}
          />
          <FormField
            type="time"
            label="Closing Time"
            value={formData.closing_time || ""}
            onChange={(v) => updateField("closing_time", v)}
          />
        </>
      )

    case "admission_requirements":
      return (
        <>
          <FormField
            type="number"
            label="Minimum Grade Aggregate"
            value={formData.minimum_aggregate || ""}
            onChange={(v) => updateField("minimum_aggregate", v)}
            placeholder="24"
          />
          <FormField
            label="Required Subjects"
            value={formData.required_subjects || ""}
            onChange={(v) => updateField("required_subjects", v)}
            placeholder="e.g., Mathematics, English"
          />
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-ink mb-1">Additional Requirements</label>
            <textarea
              value={formData.additional_requirements || ""}
              onChange={(e) => updateField("additional_requirements", e.target.value)}
              placeholder="e.g., Pass in WASSCE, Interview required"
              className="w-full px-3 py-2 border border-cocoa-200 rounded-md text-sm focus:border-cocoa-400 focus:outline-none"
              rows={3}
            />
          </div>
        </>
      )

    case "application_form":
      return (
        <>
          <CheckboxField
            label="Personal Information"
            checked={formData.include_personal || false}
            onChange={(v) => updateField("include_personal", v)}
          />
          <CheckboxField
            label="Academic Information"
            checked={formData.include_academic || false}
            onChange={(v) => updateField("include_academic", v)}
          />
          <CheckboxField
            label="WASSCE Results"
            checked={formData.include_wassce || false}
            onChange={(v) => updateField("include_wassce", v)}
          />
          <CheckboxField
            label="Document Upload"
            checked={formData.include_documents || false}
            onChange={(v) => updateField("include_documents", v)}
          />
          <CheckboxField
            label="Allow Multiple Programme Choices"
            checked={formData.allow_multiple_choices || false}
            onChange={(v) => updateField("allow_multiple_choices", v)}
          />
          <FormField
            type="number"
            label="Max Choices (if multiple allowed)"
            value={formData.max_choices || ""}
            onChange={(v) => updateField("max_choices", v)}
            placeholder="3"
          />
        </>
      )

    case "application_fee":
      return (
        <>
          <FormField
            type="number"
            label="Fee Amount"
            value={formData.fee_amount || ""}
            onChange={(v) => updateField("fee_amount", v)}
            placeholder="150"
          />
          <FormField
            label="Currency"
            value={formData.currency || ""}
            onChange={(v) => updateField("currency", v)}
            placeholder="GHS"
          />
          <FormField
            label="Payment Provider"
            value={formData.payment_provider || ""}
            onChange={(v) => updateField("payment_provider", v)}
            placeholder="e.g., Paystack, Flutterwave"
          />
          <CheckboxField
            label="Fee Waiver Available"
            checked={formData.allow_waiver || false}
            onChange={(v) => updateField("allow_waiver", v)}
          />
        </>
      )

    case "staff":
      return (
        <>
          <FormField
            label="Registrar Name"
            value={formData.registrar_name || ""}
            onChange={(v) => updateField("registrar_name", v)}
            placeholder="Full name"
          />
          <FormField
            label="Registrar Email"
            type="email"
            value={formData.registrar_email || ""}
            onChange={(v) => updateField("registrar_email", v)}
          />
          <FormField
            label="Admissions Officer Name"
            value={formData.admissions_officer_name || ""}
            onChange={(v) => updateField("admissions_officer_name", v)}
          />
          <FormField
            label="Admissions Officer Email"
            type="email"
            value={formData.admissions_officer_email || ""}
            onChange={(v) => updateField("admissions_officer_email", v)}
          />
        </>
      )

    case "student_id_configuration":
      return (
        <>
          <FormField
            label="Format Pattern"
            value={formData.format_pattern || ""}
            onChange={(v) => updateField("format_pattern", v)}
            placeholder="{SCHOOL_CODE}-{YEAR}-{SEQUENCE}"
          />
          <FormField
            type="number"
            label="Starting Sequence"
            value={formData.starting_sequence || ""}
            onChange={(v) => updateField("starting_sequence", v)}
            placeholder="1"
          />
          <CheckboxField
            label="Include Year in ID"
            checked={formData.year_inclusion || false}
            onChange={(v) => updateField("year_inclusion", v)}
          />
        </>
      )

    case "staff_id_configuration":
      return (
        <>
          <FormField
            label="Format Pattern"
            value={formData.format_pattern || ""}
            onChange={(v) => updateField("format_pattern", v)}
            placeholder="{SCHOOL_CODE}-STF-{SEQUENCE}"
          />
          <FormField
            type="number"
            label="Starting Sequence"
            value={formData.starting_sequence || ""}
            onChange={(v) => updateField("starting_sequence", v)}
            placeholder="1"
          />
        </>
      )

    case "applicant_id_configuration":
      return (
        <>
          <FormField
            label="Format Pattern"
            value={formData.format_pattern || ""}
            onChange={(v) => updateField("format_pattern", v)}
            placeholder="{SCHOOL_CODE}-APP-{YEAR}-{SEQUENCE}"
          />
          <FormField
            type="number"
            label="Starting Sequence"
            value={formData.starting_sequence || ""}
            onChange={(v) => updateField("starting_sequence", v)}
          />
          <CheckboxField
            label="Include Year in ID"
            checked={formData.year_inclusion || false}
            onChange={(v) => updateField("year_inclusion", v)}
          />
        </>
      )

    case "finance":
      return (
        <>
          <FormField
            label="Currency"
            value={formData.currency || ""}
            onChange={(v) => updateField("currency", v)}
            placeholder="GHS"
          />
          <FormField
            label="Fiscal Year Start Month"
            type="number"
            value={formData.fiscal_year_start_month || ""}
            onChange={(v) => updateField("fiscal_year_start_month", v)}
            placeholder="1"
          />
          <CheckboxField
            label="Enable Scholarships"
            checked={formData.enable_scholarships || false}
            onChange={(v) => updateField("enable_scholarships", v)}
          />
          <CheckboxField
            label="Enable Student Discounts"
            checked={formData.enable_discounts || false}
            onChange={(v) => updateField("enable_discounts", v)}
          />
        </>
      )

    case "grading":
      return (
        <>
          <FormField
            type="number"
            label="Pass Mark (%)"
            value={formData.pass_mark || ""}
            onChange={(v) => updateField("pass_mark", v)}
            placeholder="40"
          />
          <FormField
            type="number"
            label="GPA Scale"
            value={formData.gpa_scale || ""}
            onChange={(v) => updateField("gpa_scale", v)}
            placeholder="4"
          />
          <FormField
            type="number"
            label="CGPA Scale"
            value={formData.cgpa_scale || ""}
            onChange={(v) => updateField("cgpa_scale", v)}
            placeholder="4"
          />
          <CheckboxField
            label="Enable Grade Appeals"
            checked={formData.enable_appeals || false}
            onChange={(v) => updateField("enable_appeals", v)}
          />
        </>
      )

    case "graduation":
      return (
        <>
          <FormField
            type="number"
            label="Minimum Credits"
            value={formData.minimum_credits || ""}
            onChange={(v) => updateField("minimum_credits", v)}
            placeholder="120"
          />
          <FormField
            type="number"
            label="Minimum CGPA"
            value={formData.minimum_cgpa || ""}
            onChange={(v) => updateField("minimum_cgpa", v)}
            placeholder="1.5"
          />
          <CheckboxField
            label="Require Clearance"
            checked={formData.require_clearance || false}
            onChange={(v) => updateField("require_clearance", v)}
          />
          <CheckboxField
            label="Auto-generate Transcripts"
            checked={formData.auto_transcripts || false}
            onChange={(v) => updateField("auto_transcripts", v)}
          />
        </>
      )

    case "module_enablement":
      return (
        <>
          <CheckboxField
            label="Enable Admissions"
            checked={formData.admissions || true}
            onChange={(v) => updateField("admissions", v)}
          />
          <CheckboxField
            label="Enable Academics"
            checked={formData.academics || true}
            onChange={(v) => updateField("academics", v)}
          />
          <CheckboxField
            label="Enable Finance"
            checked={formData.finance || true}
            onChange={(v) => updateField("finance", v)}
          />
          <CheckboxField
            label="Enable Accommodation"
            checked={formData.accommodation || false}
            onChange={(v) => updateField("accommodation", v)}
          />
          <CheckboxField
            label="Enable Library"
            checked={formData.library || false}
            onChange={(v) => updateField("library", v)}
          />
          <CheckboxField
            label="Enable Examinations"
            checked={formData.examinations || true}
            onChange={(v) => updateField("examinations", v)}
          />
        </>
      )

    case "admission_categories":
      return (
        <>
          <FormField
            label="Category Name"
            value={formData.category_name || ""}
            onChange={(v) => updateField("category_name", v)}
            placeholder="e.g., Tertiary, WASSCE, Direct Entry"
          />
          <FormField
            type="number"
            label="Min Aggregate"
            value={formData.min_aggregate || ""}
            onChange={(v) => updateField("min_aggregate", v)}
            placeholder="e.g., 24"
          />
          <FormField
            type="number"
            label="Intake Slots"
            value={formData.intake_slots || ""}
            onChange={(v) => updateField("intake_slots", v)}
            placeholder="e.g., 100"
          />
          <CheckboxField
            label="Is Active"
            checked={formData.is_active || true}
            onChange={(v) => updateField("is_active", v)}
          />
        </>
      )

    case "role_permission":
      return (
        <>
          <FormField
            label="Role Name"
            value={formData.role_name || ""}
            onChange={(v) => updateField("role_name", v)}
            placeholder="e.g., Admissions Officer, Dean"
          />
          <FormField
            label="Role Description"
            value={formData.description || ""}
            onChange={(v) => updateField("description", v)}
            placeholder="Brief description of role"
          />
          <CheckboxField
            label="Can View Applications"
            checked={formData.can_view_applications || false}
            onChange={(v) => updateField("can_view_applications", v)}
          />
          <CheckboxField
            label="Can Approve Applications"
            checked={formData.can_approve_applications || false}
            onChange={(v) => updateField("can_approve_applications", v)}
          />
          <CheckboxField
            label="Can Manage Users"
            checked={formData.can_manage_users || false}
            onChange={(v) => updateField("can_manage_users", v)}
          />
          <CheckboxField
            label="Can Access Reports"
            checked={formData.can_access_reports || false}
            onChange={(v) => updateField("can_access_reports", v)}
          />
        </>
      )

    case "hostel":
      return (
        <>
          <FormField
            label="Hostel Name"
            value={formData.hostel_name || ""}
            onChange={(v) => updateField("hostel_name", v)}
            placeholder="e.g., North Campus Hostel"
          />
          <FormField
            label="Hostel Code"
            value={formData.hostel_code || ""}
            onChange={(v) => updateField("hostel_code", v)}
            placeholder="e.g., NCH"
          />
          <FormField
            type="number"
            label="Total Rooms"
            value={formData.total_rooms || ""}
            onChange={(v) => updateField("total_rooms", v)}
            placeholder="e.g., 50"
          />
          <FormField
            type="number"
            label="Beds per Room"
            value={formData.beds_per_room || ""}
            onChange={(v) => updateField("beds_per_room", v)}
            placeholder="e.g., 4"
          />
          <FormField
            type="number"
            label="Hostel Fee (per semester)"
            value={formData.hostel_fee || ""}
            onChange={(v) => updateField("hostel_fee", v)}
            placeholder="e.g., 500"
          />
          <CheckboxField
            label="Is Active"
            checked={formData.is_active || true}
            onChange={(v) => updateField("is_active", v)}
          />
        </>
      )

    case "library":
      return (
        <>
          <FormField
            label="Library Name"
            value={formData.library_name || ""}
            onChange={(v) => updateField("library_name", v)}
            placeholder="e.g., Main Campus Library"
          />
          <FormField
            label="Library Code"
            value={formData.library_code || ""}
            onChange={(v) => updateField("library_code", v)}
            placeholder="e.g., MCL"
          />
          <FormField
            type="number"
            label="Opening Hours (24-hour format)"
            value={formData.opening_hours || ""}
            onChange={(v) => updateField("opening_hours", v)}
            placeholder="e.g., 6"
          />
          <FormField
            type="number"
            label="Closing Hours (24-hour format)"
            value={formData.closing_hours || ""}
            onChange={(v) => updateField("closing_hours", v)}
            placeholder="e.g., 22"
          />
          <FormField
            type="number"
            label="Book Lending Duration (days)"
            value={formData.lending_duration || ""}
            onChange={(v) => updateField("lending_duration", v)}
            placeholder="e.g., 14"
          />
          <FormField
            type="number"
            label="Total Books"
            value={formData.total_books || ""}
            onChange={(v) => updateField("total_books", v)}
            placeholder="e.g., 10000"
          />
          <CheckboxField
            label="Enable Online Catalog"
            checked={formData.enable_online_catalog || true}
            onChange={(v) => updateField("enable_online_catalog", v)}
          />
        </>
      )

    default:
      return <div className="text-cocoa-500">No fields for this section</div>
  }
}

function FormField({
  label,
  value,
  onChange,
  type = "text",
  placeholder = "",
  helperText = "",
}: {
  label: string
  value: any
  onChange: (value: any) => void
  type?: string
  placeholder?: string
  helperText?: string
}) {
  return (
    <label className="space-y-1">
      <span className="block text-sm font-medium text-ink">{label}</span>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full px-3 py-2 border border-cocoa-200 rounded-md text-sm bg-white focus:border-cocoa-400 focus:outline-none"
      />
      {helperText && <span className="block text-xs text-cocoa-500">{helperText}</span>}
    </label>
  )
}

function CheckboxField({
  label,
  checked,
  onChange,
}: {
  label: string
  checked: boolean
  onChange: (checked: boolean) => void
}) {
  return (
    <label className="flex items-center gap-2 text-sm">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="rounded border-cocoa-200"
      />
      <span className="text-ink">{label}</span>
    </label>
  )
}
