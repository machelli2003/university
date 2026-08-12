import { useForm } from "react-hook-form"
import { AppShell } from "@/components/layout/AppShell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Select } from "@/components/ui/Select"
import { ErrorAlert, SuccessAlert } from "@/components/ui/Feedback"
import { useRequestLeave } from "@/hooks/useHr"
import { getErrorMessage } from "@/services/api/client"
import type { LeaveRequest } from "@/types/hr"

const LEAVE_TYPES = ["annual", "sick", "maternity", "paternity", "study", "unpaid"]

export default function RequestLeavePage() {
  const requestMutation = useRequestLeave()
  const { register, handleSubmit, reset } = useForm<LeaveRequest>({
    defaultValues: { leave_type: "annual", start_date: "", end_date: "", reason: "" },
  })

  const onSubmit = (data: LeaveRequest) => {
    requestMutation.mutate(data, { onSuccess: () => reset() })
  }

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-semibold text-ink mb-1">Request Leave</h1>
      <p className="text-cocoa-400 mb-6">Submit a leave request for HOD/Admin approval.</p>

      <Card className="max-w-lg">
        <CardHeader><CardTitle>Leave Application</CardTitle></CardHeader>
        <CardContent>
          {requestMutation.isError && <ErrorAlert message={getErrorMessage(requestMutation.error)} />}
          {requestMutation.isSuccess && <SuccessAlert message="Leave request submitted." />}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <Select label="Leave Type" {...register("leave_type")}>
              {LEAVE_TYPES.map((t) => (
                <option key={t} value={t} className="capitalize">{t}</option>
              ))}
            </Select>

            <div className="grid grid-cols-2 gap-3">
              <Input label="Start Date" type="date" {...register("start_date", { required: true })} />
              <Input label="End Date" type="date" {...register("end_date", { required: true })} />
            </div>

            <Input label="Reason" placeholder="Brief reason for leave" {...register("reason", { required: true })} />

            <Button type="submit" isLoading={requestMutation.isPending} className="w-full">
              Submit Request
            </Button>
          </form>
        </CardContent>
      </Card>
    </AppShell>
  )
}
