import { useState } from "react"
import { AppShell } from "@/components/layout/AppShell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Select } from "@/components/ui/Select"
import { Input } from "@/components/ui/Input"
import { Badge } from "@/components/ui/Badge"
import { ErrorAlert, SuccessAlert, Spinner } from "@/components/ui/Feedback"
import { useAuthStore } from "@/store/authStore"
import { useHalls, useRooms, useAllocateRoom, useReportMaintenance } from "@/hooks/useAccommodation"
import { getErrorMessage } from "@/services/api/client"

export default function AccommodationPage() {
  const studentId = useAuthStore((s) => s.studentId)
  const { data: halls } = useHalls()
  const [selectedHall, setSelectedHall] = useState("")
  const { data: rooms, isLoading: roomsLoading } = useRooms(selectedHall)
  const allocateMutation = useAllocateRoom()
  const maintenanceMutation = useReportMaintenance()
  const [issueText, setIssueText] = useState("")

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-semibold text-ink mb-1">Accommodation</h1>
      <p className="text-cocoa-400 mb-6">Book a hostel room and report maintenance issues.</p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader><CardTitle>Book a Room</CardTitle></CardHeader>
          <CardContent>
            {allocateMutation.isError && <ErrorAlert message={getErrorMessage(allocateMutation.error)} />}
            {allocateMutation.isSuccess && <SuccessAlert message="Room allocated successfully." />}

            <Select
              label="Select Hall"
              value={selectedHall}
              onChange={(e) => setSelectedHall(e.target.value)}
              className="mb-4"
            >
              <option value="">Choose a hall...</option>
              {halls?.map((h) => (
                <option key={h.id} value={h.id}>{h.name} (cap. {h.capacity})</option>
              ))}
            </Select>

            {roomsLoading && <Spinner />}

            {selectedHall && rooms && (
              <div className="space-y-2">
                {rooms.map((room) => (
                  <div
                    key={room.id}
                    className="flex items-center justify-between border border-cocoa-100 rounded-md px-4 py-3"
                  >
                    <div>
                      <p className="font-medium text-sm">Room {room.room_number}</p>
                      <p className="text-xs text-cocoa-400 capitalize">
                        {room.room_type} — {room.occupied}/{room.capacity} occupied
                      </p>
                    </div>
                    <Button
                      size="sm"
                      disabled={room.occupied >= room.capacity || !studentId}
                      isLoading={allocateMutation.isPending}
                      onClick={() =>
                        studentId &&
                        allocateMutation.mutate({
                          student_id: studentId,
                          hall_id: selectedHall,
                          room_id: room.id,
                        })
                      }
                    >
                      {room.occupied >= room.capacity ? "Full" : "Book"}
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Report Maintenance Issue</CardTitle></CardHeader>
          <CardContent>
            {maintenanceMutation.isError && <ErrorAlert message={getErrorMessage(maintenanceMutation.error)} />}
            {maintenanceMutation.isSuccess && <SuccessAlert message="Maintenance request submitted." />}

            <div className="space-y-4">
              <Select label="Hall" value={selectedHall} onChange={(e) => setSelectedHall(e.target.value)}>
                <option value="">Choose a hall...</option>
                {halls?.map((h) => (
                  <option key={h.id} value={h.id}>{h.name}</option>
                ))}
              </Select>

              <Input
                label="Describe the issue"
                placeholder="e.g. Broken window latch"
                value={issueText}
                onChange={(e) => setIssueText(e.target.value)}
              />

              <Button
                isLoading={maintenanceMutation.isPending}
                disabled={!selectedHall || !issueText}
                onClick={() =>
                  maintenanceMutation.mutate(
                    { hall_id: selectedHall, issue_description: issueText },
                    { onSuccess: () => setIssueText("") }
                  )
                }
              >
                Submit Request
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  )
}
