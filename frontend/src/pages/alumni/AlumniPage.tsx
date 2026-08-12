import { useState } from "react"
import { useForm } from "react-hook-form"
import { AppShell } from "@/components/layout/AppShell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { ErrorAlert, SuccessAlert, Spinner } from "@/components/ui/Feedback"
import { useAlumniDirectory, useRequestMentorship, useMakeDonation } from "@/hooks/useAlumni"
import { getErrorMessage } from "@/services/api/client"
import { formatCurrency } from "@/lib/utils"
import type { MakeDonationRequest } from "@/types/alumni"

export default function AlumniPage() {
  const { data: directory, isLoading } = useAlumniDirectory()
  const mentorshipMutation = useRequestMentorship()
  const donationMutation = useMakeDonation()
  const [mentorId, setMentorId] = useState("")

  const donationForm = useForm<MakeDonationRequest>({ defaultValues: { amount: 0, purpose: "" } })

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-semibold text-ink mb-1">Alumni</h1>
      <p className="text-cocoa-400 mb-6">Browse the alumni directory, request mentorship, and give back.</p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader><CardTitle>Alumni Directory</CardTitle></CardHeader>
          <CardContent>
            {isLoading && <Spinner />}
            <div className="space-y-2 max-h-80 overflow-y-auto scrollbar-thin">
              {directory?.map((a) => (
                <div key={a.id} className="border border-cocoa-100 rounded-md px-4 py-2 text-sm">
                  <p className="font-medium">{a.current_occupation || "Occupation not listed"}</p>
                  <p className="text-cocoa-400 text-xs">{a.company || "—"}</p>
                </div>
              ))}
              {directory && directory.length === 0 && (
                <p className="text-sm text-cocoa-400">No alumni profiles yet.</p>
              )}
            </div>
          </CardContent>
        </Card>

        <div className="space-y-6">
          <Card>
            <CardHeader><CardTitle>Request Mentorship</CardTitle></CardHeader>
            <CardContent>
              {mentorshipMutation.isError && <ErrorAlert message={getErrorMessage(mentorshipMutation.error)} />}
              {mentorshipMutation.isSuccess && <SuccessAlert message="Mentorship request sent." />}
              <div className="space-y-3">
                <Input
                  label="Mentor User ID"
                  placeholder="Paste the mentor's user ID"
                  value={mentorId}
                  onChange={(e) => setMentorId(e.target.value)}
                />
                <Button
                  isLoading={mentorshipMutation.isPending}
                  disabled={!mentorId}
                  onClick={() => mentorshipMutation.mutate({ mentor_id: mentorId }, { onSuccess: () => setMentorId("") })}
                >
                  Request Mentorship
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Make a Donation</CardTitle></CardHeader>
            <CardContent>
              {donationMutation.isError && <ErrorAlert message={getErrorMessage(donationMutation.error)} />}
              {donationMutation.isSuccess && <SuccessAlert message="Thank you for your donation!" />}
              <form
                onSubmit={donationForm.handleSubmit((data) =>
                  donationMutation.mutate(
                    { ...data, amount: Number(data.amount) },
                    { onSuccess: () => donationForm.reset() }
                  )
                )}
                className="space-y-3"
              >
                <Input label="Amount (GHS)" type="number" {...donationForm.register("amount", { required: true })} />
                <Input label="Purpose" placeholder="e.g. Scholarship fund" {...donationForm.register("purpose", { required: true })} />
                <Button type="submit" isLoading={donationMutation.isPending}>Donate</Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppShell>
  )
}
