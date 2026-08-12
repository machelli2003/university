import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { useForm } from "react-hook-form"
import { AppShell } from "@/components/layout/AppShell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Select } from "@/components/ui/Select"
import { Badge, statusToVariant } from "@/components/ui/Badge"
import { ErrorAlert, SuccessAlert, Spinner } from "@/components/ui/Feedback"
import { useAuthStore } from "@/store/authStore"
import {
  useMyApplication,
  useCreateApplication,
  useSubmitApplication,
  useSubmitResults,
  useVerifyWAEC,
  useAcceptOffer,
  useRejectOffer,
  useProgrammes,
} from "@/hooks/useAdmissions"
import type { ApplicationStatus } from "@/types/admissions"
import { WASSCE_GRADES, CORE_SUBJECTS } from "@/types/admissions"
import { ROUTES } from "@/constants/routes"
import { getErrorMessage } from "@/services/api/client"
import { formatDate } from "@/lib/utils"

const ADMISSION_STEP_ORDER: ApplicationStatus[] = [
  "draft",
  "submitted",
  "awaiting_results",
  "results_uploaded",
  "results_approved",
  "eligible",
  "ineligible",
  "ranked",
  "allocated",
  "waitlisted",
  "offered",
  "accepted",
  "rejected",
]

const STEP_LABELS: Record<ApplicationStatus, string> = {
  draft: "Begin application",
  submitted: "Submit exam details",
  awaiting_results: "Verify results",
  results_uploaded: "Review results",
  results_approved: "Approved results",
  eligible: "Eligible",
  ineligible: "Ineligible",
  ranked: "Ranked",
  allocated: "Allocated",
  waitlisted: "Waitlisted",
  offered: "Offer published",
  accepted: "Offer accepted",
  rejected: "Final decision",
}

export default function ApplicationStatusPage() {
  const applicantId = useAuthStore((s) => s.applicantId)
  const setApplicantId = useAuthStore((s) => s.setApplicantId)
  const setStudentId = useAuthStore((s) => s.setStudentId)

  const { data: applicant, isLoading } = useMyApplication(applicantId ?? undefined)

  useEffect(() => {
    if (applicant?.student_id) {
      setStudentId(applicant.student_id)
    }
  }, [applicant?.student_id, setStudentId])

  if (!applicantId) {
    return (
      <AppShell>
        <StartApplicationCard onCreated={(id) => setApplicantId(id)} />
      </AppShell>
    )
  }

  if (isLoading) {
    return (
      <AppShell>
        <div className="flex justify-center py-16">
          <Spinner className="h-8 w-8" />
        </div>
      </AppShell>
    )
  }

  if (!applicant) {
    return (
      <AppShell>
        <ErrorAlert message="Could not load your application." />
      </AppShell>
    )
  }

  return (
    <AppShell>
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between mb-6">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink">My Application</h1>
          <p className="text-cocoa-500 text-sm mt-1">Track your admissions journey and see the next step clearly.</p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <Badge variant={statusToVariant(applicant.status)}>{applicant.status.replace(/_/g, " ")}</Badge>
          {applicant.student_id && (
            <Link to={ROUTES.ACADEMIC_REGISTRATION} className="inline-flex">
              <Badge variant="success">Student record active</Badge>
            </Link>
          )}
        </div>
      </div>

      <AdmissionTimeline currentStatus={applicant.status} />

      <div className="space-y-6">
        <Card>
          <CardHeader><CardTitle>Applicant Details</CardTitle></CardHeader>
          <CardContent className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-cocoa-400">Name</p>
              <p className="font-medium">{applicant.first_name} {applicant.last_name}</p>
            </div>
            <div>
              <p className="text-cocoa-400">Phone</p>
              <p className="font-medium">{applicant.phone}</p>
            </div>
            <div>
              <p className="text-cocoa-400">Applied</p>
              <p className="font-medium">{formatDate(applicant.created_at)}</p>
            </div>
            <div>
              <p className="text-cocoa-400">Index Number</p>
              <p className="font-medium font-mono">{applicant.index_number || "Not submitted"}</p>
            </div>
          </CardContent>
        </Card>

        {applicant.status === "draft" && <SubmitChoicesCard applicantId={applicant.id} />}

        {["submitted", "awaiting_results"].includes(applicant.status) && (
          <VerifyWAECCard applicantId={applicant.id} />
        )}

        {["submitted", "awaiting_results", "results_uploaded"].includes(applicant.status) && (
          <SubmitResultsCard applicantId={applicant.id} />
        )}

        {['awaiting_results', 'results_uploaded', 'results_approved', 'eligible', 'ineligible', 'ranked', 'allocated', 'waitlisted', 'offered', 'rejected'].includes(applicant.status) && (
          <StatusInfoCard status={applicant.status} />
        )}

        {Object.keys(applicant.results).length > 0 && (
          <Card>
            <CardHeader><CardTitle>Submitted Results</CardTitle></CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-3 text-sm">
                {Object.entries(applicant.results).map(([subject, grade]) => (
                  <div key={subject} className="flex justify-between border-b border-cocoa-50 pb-1">
                    <span className="text-cocoa-500 capitalize">{subject.replace(/_/g, " ")}</span>
                    <span className="font-mono font-medium">{grade}</span>
                  </div>
                ))}
              </div>
              {applicant.aggregate && (
                <p className="mt-4 text-sm">
                  <span className="text-cocoa-400">Aggregate: </span>
                  <span className="font-mono font-semibold">{applicant.aggregate}</span>
                </p>
              )}
            </CardContent>
          </Card>
        )}

        {applicant.status === "offered" && (
          <div className="grid gap-6 lg:grid-cols-2">
            <AcceptOfferCard applicantId={applicant.id} />
            <RejectOfferCard applicantId={applicant.id} />
          </div>
        )}

        {applicant.status === "accepted" && (
          <>
            <Card>
              <CardContent className="space-y-3 py-6 text-center">
                <SuccessAlert message="Congratulations! You've accepted your offer. Your student record has been created." />
                {applicant.student_id && (
                  <>
                    <p className="text-sm text-cocoa-500">
                      Your student record is now active. Use your student profile to register courses and make payments.
                    </p>
                    <div className="flex flex-col gap-3 sm:flex-row sm:justify-center mt-4">
                      <Link to={ROUTES.ACADEMIC_REGISTRATION} className="inline-flex justify-center rounded-full bg-brass-600 px-5 py-2 text-sm font-semibold text-white transition hover:bg-brass-700">
                        Register Courses
                      </Link>
                      <Link to={ROUTES.FINANCE_PAYMENTS} className="inline-flex justify-center rounded-full border border-cocoa-200 bg-white px-5 py-2 text-sm font-semibold text-cocoa-700 transition hover:bg-cocoa-50">
                        Pay Fees
                      </Link>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
            {applicant.student_id && (
              <Card>
                <CardHeader>
                  <CardTitle>Student Dashboard</CardTitle>
                </CardHeader>
                <CardContent className="grid gap-3 sm:grid-cols-2">
                  <Link
                    to={ROUTES.ACADEMIC_REGISTRATION}
                    className="rounded-xl border border-cocoa-100 bg-white p-4 text-left transition hover:border-brass-200 hover:bg-brass-50"
                  >
                    <p className="text-sm font-semibold text-ink">Course Registration</p>
                    <p className="text-xs text-cocoa-500">Select and manage your semester courses.</p>
                  </Link>
                  <Link
                    to={ROUTES.FINANCE_PAYMENTS}
                    className="rounded-xl border border-cocoa-100 bg-white p-4 text-left transition hover:border-brass-200 hover:bg-brass-50"
                  >
                    <p className="text-sm font-semibold text-ink">Payments</p>
                    <p className="text-xs text-cocoa-500">Pay tuition and other campus fees.</p>
                  </Link>
                  <Link
                    to={ROUTES.LIBRARY}
                    className="rounded-xl border border-cocoa-100 bg-white p-4 text-left transition hover:border-brass-200 hover:bg-brass-50"
                  >
                    <p className="text-sm font-semibold text-ink">Library</p>
                    <p className="text-xs text-cocoa-500">Borrow books and manage loans.</p>
                  </Link>
                  <Link
                    to={ROUTES.HEALTH}
                    className="rounded-xl border border-cocoa-100 bg-white p-4 text-left transition hover:border-brass-200 hover:bg-brass-50"
                  >
                    <p className="text-sm font-semibold text-ink">Health Services</p>
                    <p className="text-xs text-cocoa-500">Book appointments and manage records.</p>
                  </Link>
                </CardContent>
              </Card>
            )}
          </>
        )}
      </div>
    </AppShell>
  )
}

function StartApplicationCard({ onCreated }: { onCreated: (id: string) => void }) {
  const createMutation = useCreateApplication()
  const { register, handleSubmit } = useForm({
    defaultValues: { first_name: "", last_name: "", phone: "", region: "" },
  })

  const onSubmit = (data: any) => {
    createMutation.mutate(data, {
      onSuccess: (applicant) => onCreated(applicant.id),
    })
  }

  return (
    <Card className="max-w-lg">
      <CardHeader><CardTitle>Start Your Application</CardTitle></CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {createMutation.isError && <ErrorAlert message={getErrorMessage(createMutation.error)} />}
          <div className="grid grid-cols-2 gap-3">
            <Input label="First name" {...register("first_name", { required: true })} />
            <Input label="Last name" {...register("last_name", { required: true })} />
          </div>
          <Input label="Phone" placeholder="0244000000" {...register("phone", { required: true })} />
          <Input label="Region" placeholder="Greater Accra" {...register("region")} />
          <Button type="submit" isLoading={createMutation.isPending}>Create Application</Button>
        </form>
      </CardContent>
    </Card>
  )
}

function SubmitChoicesCard({ applicantId }: { applicantId: string }) {
  const { data: programmes } = useProgrammes()
  const submitMutation = useSubmitApplication(applicantId)
  const { register, handleSubmit } = useForm({
    defaultValues: { index_number: "", exam_year: new Date().getFullYear(), exam_type: "WASSCE", programme_id: "" },
  })

  const onSubmit = (data: any) => {
    submitMutation.mutate({
      index_number: data.index_number,
      exam_year: Number(data.exam_year),
      exam_type: data.exam_type,
      programme_choices: [{ programme_id: data.programme_id, choice_order: 1 }],
    })
  }

  return (
    <Card>
      <CardHeader><CardTitle>Submit Programme Choice</CardTitle></CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {submitMutation.isError && <ErrorAlert message={getErrorMessage(submitMutation.error)} />}
          <Input label="Index Number" placeholder="1234567890" {...register("index_number", { required: true })} />
          <div className="grid grid-cols-2 gap-3">
            <Input label="Exam Year" type="number" {...register("exam_year", { required: true })} />
            <Select label="Exam Type" {...register("exam_type")}>
              <option value="WASSCE">WASSCE</option>
              <option value="NECO">NECO</option>
              <option value="IB">IB</option>
              <option value="A-LEVELS">A-Levels</option>
            </Select>
          </div>
          <Select label="Programme Choice" {...register("programme_id", { required: true })}>
            <option value="">Select a programme...</option>
            {programmes?.map((p) => (
              <option key={p.id} value={p.id}>{p.name} ({p.code})</option>
            ))}
          </Select>
          <Button type="submit" isLoading={submitMutation.isPending}>Submit Application</Button>
        </form>
      </CardContent>
    </Card>
  )
}

function VerifyWAECCard({ applicantId }: { applicantId: string }) {
  const verifyMutation = useVerifyWAEC(applicantId)
  const [pin, setPin] = useState("")

  return (
    <Card>
      <CardHeader><CardTitle>Verify WAEC Results</CardTitle></CardHeader>
      <CardContent>
        <p className="text-sm text-cocoa-500 mb-4">
          Enter your WAEC PIN to verify your exam record. This is a stubbed verification step for the current system.
        </p>

        {verifyMutation.isError && <ErrorAlert message={getErrorMessage(verifyMutation.error)} />}
        {verifyMutation.isSuccess && (
          <SuccessAlert message={verifyMutation.data.message || "Verification completed."} />
        )}

        <div className="grid grid-cols-1 gap-4">
          <Input
            label="WAEC PIN"
            placeholder="Enter your WAEC PIN"
            value={pin}
            onChange={(e) => setPin(e.target.value)}
          />
          <Button
            onClick={() => verifyMutation.mutate(pin)}
            isLoading={verifyMutation.isPending}
            disabled={!pin.trim()}
          >
            Verify WAEC
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

function SubmitResultsCard({ applicantId }: { applicantId: string }) {
  const submitMutation = useSubmitResults(applicantId)
  const [results, setResults] = useState<Record<string, string>>({})

  const handleGradeChange = (subject: string, grade: string) => {
    setResults((prev) => ({ ...prev, [subject]: grade }))
  }

  const missingSubjects = CORE_SUBJECTS.filter((subject) => !results[subject])
  const canSubmit = missingSubjects.length === 0

  const onSubmit = () => {
    if (!canSubmit) return
    submitMutation.mutate({ results })
  }

  return (
    <Card>
      <CardHeader><CardTitle>Submit Your Results (Manual Entry)</CardTitle></CardHeader>
      <CardContent>
        <p className="text-sm text-cocoa-500 mb-4">
          WAEC electronic verification isn't connected yet — enter your grades below.
          An admissions officer will review and approve them.
        </p>

        {submitMutation.isError && <ErrorAlert message={getErrorMessage(submitMutation.error)} />}

        <div className="grid grid-cols-2 gap-4 mb-4">
          {CORE_SUBJECTS.map((subject) => (
            <Select
              key={subject}
              label={subject.replace(/_/g, " ")}
              className="capitalize"
              value={results[subject] || ""}
              onChange={(e) => handleGradeChange(subject, e.target.value)}
            >
              <option value="">Grade...</option>
              {WASSCE_GRADES.map((g) => (
                <option key={g} value={g}>{g}</option>
              ))}
            </Select>
          ))}
        </div>

        {missingSubjects.length > 0 && (
          <p className="text-xs text-red-600 mb-4">
            Please provide grades for all core subjects before submitting.
          </p>
        )}

        <Button onClick={onSubmit} isLoading={submitMutation.isPending} disabled={!canSubmit}>
          Submit Results
        </Button>
      </CardContent>
    </Card>
  )
}

function StatusInfoCard({ status }: { status: string }) {
  const statusMessages: Record<string, string> = {
    awaiting_results: "Your exam verification is pending. Please wait while the admissions team confirms your WAEC credentials.",
    submitted: "Your application was submitted. Verify your WAEC credentials or submit your results for manual review.",
    results_uploaded: "Your results have been submitted and are awaiting admin approval.",
    results_approved: "Your results have been approved. Next, the university will determine eligibility and rank applicants.",
    eligible: "You are eligible for one or more programmes. Admissions will proceed with ranking and allocation.",
    ineligible: "Your result profile does not meet programme requirements at this time. Review your programme choices or contact admissions.",
    ranked: "Your application has been ranked. Allocation will be determined based on programme capacity.",
    allocated: "A programme has been allocated to you. The university will now publish offers.",
    waitlisted: "You have been waitlisted for your preferred programme. Admissions will notify you if a place becomes available.",
    offered: "You have been offered admission. Accept the offer to complete your enrollment.",
    rejected: "Your application has been rejected. Please contact admissions for next steps.",
  }

  return (
    <Card>
      <CardHeader><CardTitle>{status.replace(/_/g, " ")}</CardTitle></CardHeader>
      <CardContent className="py-6 text-center">
        <p className="text-cocoa-500">{statusMessages[status] ?? "Your application is in progress."}</p>
      </CardContent>
    </Card>
  )
}

function AcceptOfferCard({ applicantId }: { applicantId: string }) {
  const setStudentId = useAuthStore((s) => s.setStudentId)
  const acceptMutation = useAcceptOffer(applicantId)

  return (
    <Card className="border-brass-300">
      <CardHeader><CardTitle>🎉 You Have an Offer!</CardTitle></CardHeader>
      <CardContent>
        {acceptMutation.isError && <ErrorAlert message={getErrorMessage(acceptMutation.error)} />}
        <p className="text-sm text-cocoa-500 mb-4">
          Congratulations! Accept your offer below to complete your enrollment and register as a student.
        </p>
        <Button
          onClick={() =>
            acceptMutation.mutate(undefined, {
              onSuccess: (applicant) => {
                if (applicant.student_id) {
                  setStudentId(applicant.student_id)
                }
              },
            })
          }
          isLoading={acceptMutation.isPending}
        >
          Accept Offer
        </Button>
      </CardContent>
    </Card>
  )
}

function RejectOfferCard({ applicantId }: { applicantId: string }) {
  const rejectMutation = useRejectOffer(applicantId)
  const [reason, setReason] = useState("")

  return (
    <Card className="border-rose-200">
      <CardHeader><CardTitle>Decline Offer</CardTitle></CardHeader>
      <CardContent>
        {rejectMutation.isError && <ErrorAlert message={getErrorMessage(rejectMutation.error)} />}
        <p className="text-sm text-cocoa-500 mb-4">
          If you choose to decline this admission offer, please provide an optional reason below.
        </p>
        <Input
          label="Reason (optional)"
          placeholder="Why are you declining?"
          value={reason}
          onChange={(e) => setReason(e.target.value)}
        />
        <Button
          variant="danger"
          onClick={() => rejectMutation.mutate(reason)}
          isLoading={rejectMutation.isPending}
        >
          Decline Offer
        </Button>
      </CardContent>
    </Card>
  )
}

function AdmissionTimeline({ currentStatus }: { currentStatus: ApplicationStatus }) {
  const activeIndex = ADMISSION_STEP_ORDER.indexOf(currentStatus)

  return (
    <div className="overflow-x-auto pb-4">
      <div className="flex gap-3 min-w-max">
        {ADMISSION_STEP_ORDER.map((step, index) => {
          const completed = index <= activeIndex
          return (
            <div
              key={step}
              className={`min-w-[11rem] rounded-2xl border px-4 py-3 transition ${
                completed ? "border-brass-200 bg-brass-50" : "border-cocoa-100 bg-white"
              }`}
            >
              <div className="flex items-center gap-3">
                <div
                  className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-semibold ${
                    completed ? "bg-brass-600 text-white" : "bg-cocoa-100 text-cocoa-500"
                  }`}
                >
                  {completed ? "✓" : index + 1}
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-cocoa-500">
                    {STEP_LABELS[step]}
                  </p>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
