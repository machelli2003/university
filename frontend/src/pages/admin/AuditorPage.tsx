import { useMemo, useState, useEffect } from "react"
import { AppShell } from "@/components/layout/AppShell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Input } from "@/components/ui/Input"
import { Select } from "@/components/ui/Select"
import { Button } from "@/components/ui/Button"
import { useAuditSummary, useAuditList } from "@/hooks/useAudit"
import { auditApi } from "@/services/api/audit"
import { useAuthStore } from "@/store/authStore"
import { formatDistanceToNow } from "date-fns"

export default function AuditorPage() {
  const auditQuery = useAuditSummary()
  const user = useAuthStore((s) => s.user)
  const [eventFilter, setEventFilter] = useState<string>("")
  const [search, setSearch] = useState<string>("")
  const [startDate, setStartDate] = useState<string>("")
  const [endDate, setEndDate] = useState<string>("")
  const [exportJobId, setExportJobId] = useState<string | null>(null)
  const [exportStatus, setExportStatus] = useState<string | null>(null)

  useEffect(() => {
    if (!exportJobId) return
    let cancelled = false
    const poll = async () => {
      try {
        const status = await auditApi.getExportStatus(exportJobId)
        setExportStatus(status.status || status)
        if (status.status === "ready") {
          const blob = await auditApi.downloadExport(exportJobId)
          const url = window.URL.createObjectURL(new Blob([blob]))
          const a = document.createElement('a')
          a.href = url
          a.download = 'audits.csv'
          document.body.appendChild(a)
          a.click()
          a.remove()
          window.URL.revokeObjectURL(url)
          setExportJobId(null)
          setExportStatus(null)
        } else if (status.status === "failed") {
          alert('Export failed: ' + (status.error || 'unknown'))
          setExportJobId(null)
          setExportStatus(null)
        } else if (!cancelled) {
          setTimeout(poll, 2000)
        }
      } catch (e) {
        if (!cancelled) setTimeout(poll, 3000)
      }
    }
    poll()
    return () => { cancelled = true }
  }, [exportJobId])
  const [expandedId, setExpandedId] = useState<string | null>(null)

  const eventTypes = useMemo(() => Object.keys(auditQuery.data?.event_types ?? {}), [auditQuery.data])

  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(25)

  const listQuery = useAuditList(page, pageSize, {
    event_type: eventFilter || undefined,
    performed_by: search || undefined,
    tenant_id: user?.tenant_id || undefined,
    start_date: startDate || undefined,
    end_date: endDate || undefined,
  })

  const filtered = useMemo(() => listQuery.data?.events ?? [], [listQuery.data])

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink mb-1">Auditor Dashboard</h1>
          <p className="text-cocoa-400 mb-6">Review compliance, financial records, and audit trails for the university.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Financial Audit</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-cocoa-500">Inspect payments, fee records, and spending to ensure transparent financial controls.</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Compliance Review</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-cocoa-500">Verify process compliance, access logs, and audit reports for academic and administrative systems.</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Audit Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-cocoa-500">Capture findings, document exceptions, and share audit notes with leadership teams.</p>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Recent Audit Events</CardTitle>
          </CardHeader>
          <CardContent>
            {auditQuery.isLoading && <p>Loading audit summary...</p>}
            {auditQuery.isError && <p className="text-sm text-red-600">Unable to load audit data.</p>}
            {auditQuery.data && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="rounded-lg border border-cocoa-100 p-4">
                    <p className="text-sm text-cocoa-500">Total Events</p>
                    <p className="text-2xl font-semibold text-ink">{auditQuery.data.total_events}</p>
                  </div>
                  <div className="rounded-lg border border-cocoa-100 p-4">
                    <p className="text-sm text-cocoa-500">Event Types</p>
                    <ul className="mt-2 text-sm text-cocoa-700 space-y-1">
                      {Object.entries(auditQuery.data.event_types).map(([eventType, count]) => (
                        <li key={eventType} className="capitalize">{eventType}: {count}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-4 gap-3 items-end">
                  <Select value={eventFilter} onChange={(e) => setEventFilter(e.target.value)}>
                    <option value="">All Event Types</option>
                    {eventTypes.map((t) => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </Select>
                  <Input placeholder="Search by user, entity id, action..." value={search} onChange={(e) => setSearch(e.target.value)} />
                  <div className="flex space-x-2">
                    <Input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
                    <Input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
                  </div>
                  <Button onClick={() => { setEventFilter(""); setSearch("") }} variant="secondary">Clear</Button>
                </div>

                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <div className="text-sm text-cocoa-500">Showing {listQuery.data ? listQuery.data.events.length : 0} of {listQuery.data ? listQuery.data.total : 0}</div>
                    <div>
                      <Button variant="ghost" onClick={async () => {
                        const params: Record<string, any> = {
                          event_type: eventFilter || undefined,
                          performed_by: search || undefined,
                          tenant_id: user?.tenant_id || undefined,
                          start_date: startDate || undefined,
                          end_date: endDate || undefined,
                        }

                        try {
                          // start background export (server will stream directly for small sets)
                          const res = await auditApi.startExport(params)
                          if (res && res.job_id) {
                            setExportJobId(res.job_id)
                            setExportStatus("pending")
                          } else {
                            // fallback: try direct download
                            const blob = await auditApi.exportAudits(params)
                            const url = window.URL.createObjectURL(new Blob([blob]))
                            const a = document.createElement('a')
                            a.href = url
                            a.download = 'audits.csv'
                            document.body.appendChild(a)
                            a.click()
                            a.remove()
                            window.URL.revokeObjectURL(url)
                          }
                        } catch (err: any) {
                          // attempt direct download as fallback
                          try {
                            const blob = await auditApi.exportAudits(params)
                            const url = window.URL.createObjectURL(new Blob([blob]))
                            const a = document.createElement('a')
                            a.href = url
                            a.download = 'audits.csv'
                            document.body.appendChild(a)
                            a.click()
                            a.remove()
                            window.URL.revokeObjectURL(url)
                          } catch (e) {
                            alert('Unable to start export')
                          }
                        }
                      }}>Export CSV</Button>
                    </div>
                  </div>

                  {listQuery.isLoading && <p>Loading events...</p>}

                  {filtered.map((event) => {
                    const key = `${event.event_type}-${event.entity_id}-${event.created_at}`
                    const expanded = expandedId === key
                    return (
                      <div key={key} className="rounded-lg border border-cocoa-100 p-4">
                        <div className="flex justify-between items-start">
                          <div>
                            <p className="text-sm font-semibold text-ink">{event.action}</p>
                            <p className="text-xs text-cocoa-500">{event.event_type} · {event.entity_type} · {event.entity_id || "N/A"}</p>
                            <p className="text-xs text-cocoa-400">{event.performed_by || "Unknown"} · {formatDistanceToNow(new Date(event.created_at), { addSuffix: true })}</p>
                          </div>
                          <div>
                            <Button size="sm" onClick={() => setExpandedId(expanded ? null : key)}>{expanded ? "Hide details" : "View details"}</Button>
                          </div>
                        </div>
                        {expanded && (
                          <pre className="mt-3 overflow-auto text-xs bg-surface p-3 rounded">{JSON.stringify(event.details || {}, null, 2)}</pre>
                        )}
                      </div>
                    )
                  })}
                  {filtered.length === 0 && <p className="text-sm text-cocoa-400">No audit events match the filters.</p>}

                  <div className="flex items-center justify-between">
                    <div>
                      <Button variant="secondary" onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}>Previous</Button>
                      <Button variant="secondary" onClick={() => setPage((p) => p + 1)} className="ml-2" disabled={listQuery.data ? (page * pageSize >= listQuery.data.total) : false}>Next</Button>
                    </div>
                    <div className="text-sm text-cocoa-500">Page {page} · Page size
                      <select value={pageSize} onChange={(e) => { setPageSize(parseInt(e.target.value)); setPage(1) }} className="ml-2">
                        <option value={10}>10</option>
                        <option value={25}>25</option>
                        <option value={50}>50</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </AppShell>
  )
}
