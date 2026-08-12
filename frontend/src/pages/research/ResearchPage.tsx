import { useForm } from "react-hook-form"
import { AppShell } from "@/components/layout/AppShell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { ErrorAlert, SuccessAlert, Spinner } from "@/components/ui/Feedback"
import {
  useCreateProposal,
  useCreateGrant,
  useAddPublication,
  useMyPublications,
} from "@/hooks/useResearch"
import { getErrorMessage } from "@/services/api/client"
import type { CreateProposalRequest, CreateGrantRequest, CreatePublicationRequest } from "@/types/research"

export default function ResearchPage() {
  const proposalMutation = useCreateProposal()
  const grantMutation = useCreateGrant()
  const publicationMutation = useAddPublication()
  const { data: publications } = useMyPublications()

  const proposalForm = useForm<CreateProposalRequest>({ defaultValues: { title: "", description: "" } })
  const grantForm = useForm<CreateGrantRequest>({ defaultValues: { title: "", amount: 0 } })
  const pubForm = useForm<CreatePublicationRequest>({
    defaultValues: { title: "", journal: "", publication_date: "", doi: "" },
  })

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-semibold text-ink mb-1">Research</h1>
      <p className="text-cocoa-400 mb-6">Submit proposals, track grants, and log publications.</p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader><CardTitle>Submit Research Proposal</CardTitle></CardHeader>
          <CardContent>
            {proposalMutation.isError && <ErrorAlert message={getErrorMessage(proposalMutation.error)} />}
            {proposalMutation.isSuccess && <SuccessAlert message="Proposal submitted for review." />}
            <form
              onSubmit={proposalForm.handleSubmit((data) =>
                proposalMutation.mutate(data, { onSuccess: () => proposalForm.reset() })
              )}
              className="space-y-3"
            >
              <Input label="Title" {...proposalForm.register("title", { required: true })} />
              <Input label="Description" {...proposalForm.register("description", { required: true })} />
              <Button type="submit" isLoading={proposalMutation.isPending}>Submit Proposal</Button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Register a Grant</CardTitle></CardHeader>
          <CardContent>
            {grantMutation.isError && <ErrorAlert message={getErrorMessage(grantMutation.error)} />}
            {grantMutation.isSuccess && <SuccessAlert message="Grant registered." />}
            <form
              onSubmit={grantForm.handleSubmit((data) =>
                grantMutation.mutate({ ...data, amount: Number(data.amount) }, { onSuccess: () => grantForm.reset() })
              )}
              className="space-y-3"
            >
              <Input label="Grant Title" {...grantForm.register("title", { required: true })} />
              <Input label="Amount (GHS)" type="number" {...grantForm.register("amount", { required: true })} />
              <Button type="submit" isLoading={grantMutation.isPending}>Register Grant</Button>
            </form>
          </CardContent>
        </Card>
      </div>

      <Card className="mt-6">
        <CardHeader><CardTitle>Add Publication</CardTitle></CardHeader>
        <CardContent>
          {publicationMutation.isError && <ErrorAlert message={getErrorMessage(publicationMutation.error)} />}
          {publicationMutation.isSuccess && <SuccessAlert message="Publication added." />}
          <form
            onSubmit={pubForm.handleSubmit((data) =>
              publicationMutation.mutate(data, { onSuccess: () => pubForm.reset() })
            )}
            className="grid grid-cols-2 gap-3 mb-6"
          >
            <Input label="Title" {...pubForm.register("title", { required: true })} />
            <Input label="Journal" {...pubForm.register("journal", { required: true })} />
            <Input label="Publication Date" type="date" {...pubForm.register("publication_date", { required: true })} />
            <Input label="DOI (optional)" {...pubForm.register("doi")} />
            <Button type="submit" isLoading={publicationMutation.isPending} className="col-span-2">
              Add Publication
            </Button>
          </form>

          <h3 className="text-sm font-medium text-cocoa-500 mb-2">My Publications</h3>
          <div className="space-y-2">
            {publications?.map((p) => (
              <div key={p.id} className="border border-cocoa-100 rounded-md px-4 py-2 text-sm">
                <p className="font-medium">{p.title}</p>
                <p className="text-cocoa-400 text-xs">{p.journal}</p>
              </div>
            ))}
            {publications && publications.length === 0 && (
              <p className="text-sm text-cocoa-400">No publications logged yet.</p>
            )}
          </div>
        </CardContent>
      </Card>
    </AppShell>
  )
}
