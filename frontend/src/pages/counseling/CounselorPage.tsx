import React, { useState } from "react"
import { AppShell } from "@/components/layout/AppShell"
import { usePendingCounsel, useReplyCounsel } from "@/hooks/useCounseling"
import { useToast } from "@/components/ui/Toast"
import { getErrorMessage } from "@/services/api/client"

export default function CounselorPage() {
  const { data: pending, refetch } = usePendingCounsel()
  const reply = useReplyCounsel()
  const [responseMap, setResponseMap] = useState<Record<string,string>>({})
  const [error, setError] = useState<string | null>(null)
  const toast = useToast()

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-semibold text-ink mb-2">Counselor Inbox</h1>
      {error && <div className="text-red-500">{error}</div>}

      <div className="space-y-3">
        {pending?.map(p => (
          <div key={p.id} className="border p-3 rounded">
            <div className="font-medium">{p.subject}</div>
            <div className="text-sm text-cocoa-400">{p.message}</div>
            <div className="mt-2 flex gap-2">
              <input value={responseMap[p.id] || ''} onChange={(e)=> setResponseMap({...responseMap, [p.id]: e.target.value})} placeholder="Your response" className="input flex-1" />
              <button className="btn" onClick={async ()=> { try { if (!responseMap[p.id]) throw new Error('Response is required'); await reply.mutateAsync({ id: p.id, response: responseMap[p.id] || '' }); refetch(); toast.show({ message: 'Response sent', type: 'success' }) } catch (err) { const msg = getErrorMessage(err); setError(msg); toast.show({ message: msg, type: 'error' }) } }}>Send</button>
            </div>
          </div>
        ))}
      </div>
    </AppShell>
  )
}
