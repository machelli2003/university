import { useState } from "react"
import { useForm } from "react-hook-form"
import { AppShell } from "@/components/layout/AppShell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { ErrorAlert, SuccessAlert, Spinner } from "@/components/ui/Feedback"
import { useAuthStore } from "@/store/authStore"
import { useCreateHealthRecord, useHealthRecord, useBookAppointment, useRequestCounseling } from "@/hooks/useHealth"
import { getErrorMessage } from "@/services/api/client"
import type { CreateHealthRecordRequest, BookAppointmentRequest } from "@/types/health"

export default function HealthServicesPage() {
  const studentId = useAuthStore((s) => s.studentId)
  const { data: record } = useHealthRecord(studentId)
  const recordMutation = useCreateHealthRecord()
  const appointmentMutation = useBookAppointment()
  const counselingMutation = useRequestCounseling()
  const [counselingTopic, setCounselingTopic] = useState("")

  const { register: registerRecord, handleSubmit: handleRecordSubmit } = useForm<CreateHealthRecordRequest>({
    defaultValues: { student_id: studentId ?? "", emergency_contact: "", emergency_phone: "" },
  })

  const { register: registerAppt, handleSubmit: handleApptSubmit, reset: resetAppt } = useForm<BookAppointmentRequest>({
    defaultValues: { student_id: studentId ?? "", appointment_date: "", reason: "" },
  })

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-semibold text-ink mb-1">Health Services</h1>
      <p className="text-cocoa-400 mb-6">Manage your health record, clinic appointments, and counseling requests.</p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader><CardTitle>Health Record</CardTitle></CardHeader>
          <CardContent>
            {record ? (
              <div className="space-y-2 text-sm">
                <p><span className="text-cocoa-400">Blood Group: </span>{record.blood_group || "—"}</p>
                <p><span className="text-cocoa-400">Allergies: </span>{record.allergies || "None recorded"}</p>
                <p><span className="text-cocoa-400">Conditions: </span>{record.medical_conditions || "None recorded"}</p>
              </div>
            ) : (
              <form
                onSubmit={handleRecordSubmit((data) => recordMutation.mutate({ ...data, student_id: studentId ?? "" }))}
                className="space-y-3"
              >
                {recordMutation.isError && <ErrorAlert message={getErrorMessage(recordMutation.error)} />}
                {recordMutation.isSuccess && <SuccessAlert message="Health record created." />}
                <Input label="Blood Group" placeholder="O+" {...registerRecord("blood_group")} />
                <Input label="Allergies" placeholder="None" {...registerRecord("allergies")} />
                <Input label="Medical Conditions" placeholder="None" {...registerRecord("medical_conditions")} />
                <Input label="Emergency Contact Name" {...registerRecord("emergency_contact", { required: true })} />
                <Input label="Emergency Contact Phone" {...registerRecord("emergency_phone", { required: true })} />
                <Button type="submit" isLoading={recordMutation.isPending} disabled={!studentId}>
                  Save Record
                </Button>
                {!studentId && (
                  <p className="text-xs text-cocoa-500 mt-2">
                    Your student record must be active before health services can be linked.
                  </p>
                )}
              </form>
            )}
          </CardContent>
        </Card>

        <div className="space-y-6">
          <Card>
            <CardHeader><CardTitle>Book Clinic Appointment</CardTitle></CardHeader>
            <CardContent>
              {appointmentMutation.isError && <ErrorAlert message={getErrorMessage(appointmentMutation.error)} />}
              {appointmentMutation.isSuccess && <SuccessAlert message="Appointment booked." />}
              <form
                onSubmit={handleApptSubmit((data) => {
                  appointmentMutation.mutate({ ...data, student_id: studentId ?? "" }, { onSuccess: () => resetAppt() })
                })}
                className="space-y-3"
              >
                <Input label="Preferred Date" type="datetime-local" {...registerAppt("appointment_date", { required: true })} />
                <Input label="Reason" placeholder="e.g. Fever, checkup" {...registerAppt("reason", { required: true })} />
                <Button type="submit" isLoading={appointmentMutation.isPending} disabled={!studentId}>Book Appointment</Button>
                {!studentId && (
                  <p className="text-xs text-cocoa-500 mt-2">
                    Accept your offer first to activate your student record before booking an appointment.
                  </p>
                )}
              </form>
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Request Counseling</CardTitle></CardHeader>
            <CardContent>
              {counselingMutation.isError && <ErrorAlert message={getErrorMessage(counselingMutation.error)} />}
              {counselingMutation.isSuccess && <SuccessAlert message="Counseling request submitted confidentially." />}
              <div className="space-y-3">
                <Input
                  label="Topic (optional)"
                  placeholder="Leave blank to stay anonymous about the topic"
                  value={counselingTopic}
                  onChange={(e) => setCounselingTopic(e.target.value)}
                />
                <Button
                  isLoading={counselingMutation.isPending}
                  onClick={() =>
                    counselingMutation.mutate(
                      { topic: counselingTopic || undefined, is_anonymous: true },
                      { onSuccess: () => setCounselingTopic("") }
                    )
                  }
                  disabled={!studentId}
                >
                  Request Counseling
                </Button>
                {!studentId && (
                  <p className="text-xs text-cocoa-500 mt-2">
                    A student record is required before counseling requests can be submitted.
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppShell>
  )
}
