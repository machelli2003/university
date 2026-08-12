import { useForm } from "react-hook-form"
import { AppShell } from "@/components/layout/AppShell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { ErrorAlert, SuccessAlert, Spinner } from "@/components/ui/Feedback"
import { useCampaigns, useCreateCampaign } from "@/hooks/useCommunication"
import { getErrorMessage } from "@/services/api/client"
import type { CreateCampaignRequest } from "@/types/communication"

export default function CampaignsPage() {
  const { data: campaigns, isLoading } = useCampaigns()
  const createMutation = useCreateCampaign()
  const { register, handleSubmit, reset } = useForm<CreateCampaignRequest>({
    defaultValues: { name: "", message: "", target_role: "" },
  })

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-semibold text-ink mb-1">Campaigns</h1>
      <p className="text-cocoa-400 mb-6">Send announcements to groups of users.</p>

      <Card className="mb-6">
        <CardHeader><CardTitle>New Campaign</CardTitle></CardHeader>
        <CardContent>
          {createMutation.isError && <ErrorAlert message={getErrorMessage(createMutation.error)} />}
          {createMutation.isSuccess && <SuccessAlert message="Campaign created." />}
          <form
            onSubmit={handleSubmit((data) => createMutation.mutate(data, { onSuccess: () => reset() }))}
            className="space-y-3"
          >
            <Input label="Campaign Name" {...register("name", { required: true })} />
            <Input label="Message" {...register("message", { required: true })} />
            <Input label="Target Role (optional)" placeholder="e.g. student" {...register("target_role")} />
            <Button type="submit" isLoading={createMutation.isPending}>Create Campaign</Button>
          </form>
        </CardContent>
      </Card>

      {isLoading && <Spinner />}
      <div className="space-y-2">
        {campaigns?.map((c) => (
          <Card key={c.id}>
            <CardContent className="py-3">
              <p className="font-medium text-sm">{c.name}</p>
              <p className="text-xs text-cocoa-400">{c.message}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </AppShell>
  )
}
