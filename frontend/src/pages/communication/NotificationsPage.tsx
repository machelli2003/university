import { useNavigate } from "react-router-dom"
import { AppShell } from "@/components/layout/AppShell"
import { Card, CardContent } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Badge } from "@/components/ui/Badge"
import { Spinner } from "@/components/ui/Feedback"
import { useMyNotifications, useMarkAsRead } from "@/hooks/useCommunication"

export default function NotificationsPage() {
  const navigate = useNavigate()
  const { data: notifications, isLoading } = useMyNotifications()
  const markReadMutation = useMarkAsRead()

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-semibold text-ink mb-1">Notifications</h1>
      <p className="text-cocoa-400 mb-6">Announcements and updates addressed to you.</p>

      {isLoading && <div className="flex justify-center py-16"><Spinner className="h-8 w-8" /></div>}

      <div className="space-y-2">
        {notifications?.map((n) => (
          <Card 
            key={n.id} 
            className={`${n.is_read ? "opacity-60" : ""} ${n.target_url ? "cursor-pointer hover:shadow-md transition-shadow" : ""}`}
            onClick={() => n.target_url && navigate(n.target_url)}
          >
            <CardContent className="flex items-center justify-between py-3">
              <div>
                <div className="flex items-center gap-2">
                  <p className="font-medium text-sm">{n.title}</p>
                  {!n.is_read && <Badge variant="info">New</Badge>}
                </div>
                <p className="text-xs text-cocoa-400 mt-0.5">{n.message}</p>
              </div>
              {!n.is_read && (
                <Button size="sm" variant="ghost" onClick={(e) => {
                  e.stopPropagation()
                  markReadMutation.mutate(n.id)
                }}>
                  Mark read
                </Button>
              )}
            </CardContent>
          </Card>
        ))}
        {notifications && notifications.length === 0 && (
          <Card><CardContent className="text-center text-cocoa-400 py-8">No notifications yet.</CardContent></Card>
        )}
      </div>
    </AppShell>
  )
}
