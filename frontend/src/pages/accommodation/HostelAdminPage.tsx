import React, { useEffect, useState } from "react"
import { AppShell } from "@/components/layout/AppShell"
import { accommodationApi } from "@/services/api/accommodation"
import { usePendingMaintenance, useHalls, useRooms, useAllocateRoom, useReportMaintenance, useAssignMaintenance, useResolveMaintenance, useOccupancySummary, useRoomOccupants, useDeallocateRoom } from "@/hooks/useAccommodation"
import { getErrorMessage } from "@/services/api/client"
import { useToast } from "@/components/ui/Toast"

export default function HostelAdminPage() {
  const { data: halls } = useHalls()
  const [selectedHall, setSelectedHall] = useState("")
  const { data: rooms } = useRooms(selectedHall)
  const { data: summary } = useOccupancySummary()
  const [selectedRoomForAllocation, setSelectedRoomForAllocation] = useState(rooms?.[0]?.id ?? "")
  const [selectedRoomForOccupants, setSelectedRoomForOccupants] = useState(rooms?.[0]?.id ?? "")
  const { data: roomOccupants } = useRoomOccupants(selectedRoomForOccupants)
  const [newHall, setNewHall] = useState({ name: "", capacity: 0, gender: "" })
  const [newRoom, setNewRoom] = useState({ hall_id: "", room_number: "", room_type: "", capacity: 1 })
  const { data: pending, refetch: refetchPending } = usePendingMaintenance()
  const reportMaintenance = useReportMaintenance()
  const assignMaintenance = useAssignMaintenance()
  const resolveMaintenance = useResolveMaintenance()
  const [assigneeMap, setAssigneeMap] = useState<Record<string,string>>({})
  const toast = useToast()
  const [error, setError] = useState<string | null>(null)
  const allocateRoom = useAllocateRoom()
  const deallocateRoom = useDeallocateRoom()
  const [allocStudentId, setAllocStudentId] = useState("")
  const [deallocStudentId, setDeallocStudentId] = useState("")
  const [maintenanceIssue, setMaintenanceIssue] = useState("")

  useEffect(() => {
    if (rooms && rooms.length) {
      setSelectedRoomForAllocation(rooms[0].id)
      setSelectedRoomForOccupants(rooms[0].id)
    }
  }, [rooms])

  async function createHall(e: React.FormEvent) {
    e.preventDefault()
    try {
      if (!newHall.name) throw new Error('Hall name is required')
      if (newHall.capacity <= 0) throw new Error('Capacity must be > 0')
      await accommodationApi.createHall(newHall)
      setNewHall({ name: "", capacity: 0, gender: "" })
      // refetch handled by useHalls cache in real app
      toast.show({ message: 'Hall created', type: 'success' })
    } catch (err) {
      const msg = getErrorMessage(err)
      setError(msg)
      toast.show({ message: msg, type: 'error' })
    }
  }

  async function createRoom(e: React.FormEvent) {
    e.preventDefault()
    try {
      if (!newRoom.hall_id) throw new Error('Select a hall')
      if (!newRoom.room_number) throw new Error('Room number required')
      await accommodationApi.createRoom(newRoom)
      setNewRoom({ hall_id: "", room_number: "", room_type: "", capacity: 1 })
      // refetch handled by useRooms
      toast.show({ message: 'Room created', type: 'success' })
    } catch (err) {
      const msg = getErrorMessage(err)
      setError(msg)
      toast.show({ message: msg, type: 'error' })
    }
  }

  async function handleAllocate(e: React.FormEvent) {
    e.preventDefault()
    try {
      if (!allocStudentId) throw new Error('Student ID required')
      if (!selectedHall) throw new Error('Select a hall')
      if (!selectedRoomForAllocation) throw new Error('Select a room')
      await allocateRoom.mutateAsync({ student_id: allocStudentId, hall_id: selectedHall, room_id: selectedRoomForAllocation })
      setAllocStudentId("")
      toast.show({ message: 'Student allocated', type: 'success' })
    } catch (err) {
      const msg = getErrorMessage(err)
      setError(msg)
      toast.show({ message: msg, type: 'error' })
    }
  }

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-semibold text-ink mb-1">Hostel Administration</h1>
      {error && <p className="text-red-500">{error}</p>}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div>
          <h2 className="font-semibold mb-2">Create Hall</h2>
          <form onSubmit={createHall} className="space-y-2">
            <input value={newHall.name} onChange={(e)=> setNewHall({...newHall, name: e.target.value})} placeholder="Hall name" className="w-full input" />
            <input type="number" value={newHall.capacity} onChange={(e)=> setNewHall({...newHall, capacity: Number(e.target.value)})} placeholder="Capacity" className="w-full input" />
            <input value={newHall.gender} onChange={(e)=> setNewHall({...newHall, gender: e.target.value})} placeholder="Gender (optional)" className="w-full input" />
            <button className="btn btn-primary" type="submit">Create Hall</button>
          </form>

          <h2 className="font-semibold mt-6 mb-2">Create Room</h2>
          <form onSubmit={createRoom} className="space-y-2">
            <select value={newRoom.hall_id} onChange={(e)=> setNewRoom({...newRoom, hall_id: e.target.value})} className="w-full input">
              <option value="">Select hall</option>
              {halls?.map(h => (<option value={h.id} key={h.id}>{h.name}</option>))}
            </select>
            <input value={newRoom.room_number} onChange={(e)=> setNewRoom({...newRoom, room_number: e.target.value})} placeholder="Room number" className="w-full input" />
            <input value={newRoom.room_type} onChange={(e)=> setNewRoom({...newRoom, room_type: e.target.value})} placeholder="Room type" className="w-full input" />
            <input type="number" value={newRoom.capacity} onChange={(e)=> setNewRoom({...newRoom, capacity: Number(e.target.value)})} placeholder="Capacity" className="w-full input" />
            <button className="btn btn-primary" type="submit">Create Room</button>
          </form>
        </div>

        <div className="col-span-2 space-y-6">
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            <div className="border rounded p-4">
              <h2 className="font-semibold mb-2">Hostel Summary</h2>
              <div className="space-y-2">
                <div>Total halls: {summary?.total_halls ?? 0}</div>
                <div>Total rooms: {summary?.total_rooms ?? 0}</div>
                <div>Total capacity: {summary?.total_capacity ?? 0}</div>
                <div>Occupied: {summary?.total_occupied ?? 0}</div>
                <div>Vacancy rate: {(summary?.vacancy_rate ?? 0).toFixed(2)}</div>
              </div>
            </div>

            <div className="border rounded p-4">
              <h2 className="font-semibold mb-2">Halls</h2>
              <div className="space-y-2">
                {halls?.map(h => (
                  <div key={h.id} className="rounded border p-3 flex justify-between items-center">
                    <div>
                      <div className="font-medium">{h.name}</div>
                      <div className="text-sm text-cocoa-400">Capacity: {h.capacity}</div>
                    </div>
                    <button className="btn btn-sm" onClick={() => {
                      setSelectedHall(h.id)
                      setSelectedRoomForAllocation(rooms?.[0]?.id ?? "")
                      setSelectedRoomForOccupants(rooms?.[0]?.id ?? "")
                    }}>View rooms</button>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {selectedHall && (
            <div className="border rounded p-4">
              <h3 className="font-semibold mb-3">Rooms in selected hall</h3>
              <div className="space-y-2">
                {rooms?.map(r => (
                  <div key={r.id} className="rounded border p-3 flex justify-between items-center">
                    <div>
                      <div className="font-medium">Room {r.room_number}</div>
                      <div className="text-sm text-cocoa-400">{r.room_type} — {r.occupied}/{r.capacity}</div>
                    </div>
                    <button className="btn btn-sm" onClick={() => setSelectedRoomForOccupants(r.id)}>View occupants</button>
                  </div>
                ))}
              </div>

              <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-4">
                <div className="border rounded p-4">
                  <h4 className="font-semibold mb-2">Allocate Student</h4>
                  <form onSubmit={handleAllocate} className="space-y-3">
                    <input value={allocStudentId} onChange={(e)=> setAllocStudentId(e.target.value)} placeholder="Student ID" className="w-full input" />
                    <select value={selectedRoomForAllocation} onChange={(e)=> setSelectedRoomForAllocation(e.target.value)} className="w-full input">
                      <option value="">Select room</option>
                      {rooms?.map(r => (
                        <option key={r.id} value={r.id}>{r.room_number} — {r.room_type} ({r.occupied}/{r.capacity})</option>
                      ))}
                    </select>
                    <button className="btn btn-primary w-full" type="submit">Allocate</button>
                  </form>
                </div>

                <div className="border rounded p-4">
                  <h4 className="font-semibold mb-2">Deallocate Student</h4>
                  <form onSubmit={async (e) => {
                    e.preventDefault()
                    try {
                      if (!deallocStudentId) throw new Error('Student ID required')
                      await deallocateRoom.mutateAsync({ student_id: deallocStudentId })
                      setDeallocStudentId("")
                      toast.show({ message: 'Student deallocated', type: 'success' })
                    } catch (err) {
                      toast.show({ message: getErrorMessage(err), type: 'error' })
                    }
                  }} className="space-y-3">
                    <input value={deallocStudentId} onChange={(e)=> setDeallocStudentId(e.target.value)} placeholder="Student ID" className="w-full input" />
                    <button className="btn btn-secondary w-full" type="submit">Deallocate</button>
                  </form>
                </div>
              </div>

              <div className="mt-6">
                <h4 className="font-semibold mb-2">Selected room occupants</h4>
                {roomOccupants?.length ? (
                  <div className="space-y-2">
                    {roomOccupants.map(p => (
                      <div key={p.student_id} className="rounded border p-3">
                        <div className="font-medium">Student {p.student_id}</div>
                        <div className="text-sm text-cocoa-400">Active: {p.is_active ? 'Yes' : 'No'}</div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-cocoa-500">No occupants or no room selected.</div>
                )}
              </div>
            </div>
          )}

          <div className="border rounded p-4">
            <h3 className="font-semibold mb-2">Pending maintenance</h3>
            <button className="btn btn-sm mb-2" onClick={() => refetchPending()}>Refresh</button>
            <div className="space-y-2">
              {pending?.map(p => (
                <div key={p.id} className="border rounded p-3">
                  <div className="font-medium">{p.issue_description}</div>
                  <div className="text-sm text-cocoa-400">Status: {p.status}</div>
                  <div className="text-sm text-cocoa-400">Hall: {p.hall_id}</div>
                  <div className="flex flex-wrap gap-2 mt-3">
                    <input value={assigneeMap[p.id] || ''} onChange={(e)=> setAssigneeMap({...assigneeMap, [p.id]: e.target.value})} placeholder="Assignee ID" className="input flex-1" />
                    <button className="btn" onClick={async () => {
                      try {
                        if (!assigneeMap[p.id]) throw new Error('Assignee required')
                        await assignMaintenance.mutateAsync({ id: p.id, assignee: assigneeMap[p.id] || '' })
                        refetchPending()
                        toast.show({ message: 'Assigned', type: 'success' })
                      } catch (err) {
                        toast.show({ message: getErrorMessage(err), type: 'error' })
                      }
                    }}>Assign</button>
                    <button className="btn btn-success" onClick={async () => {
                      try {
                        await resolveMaintenance.mutateAsync(p.id)
                        refetchPending()
                        toast.show({ message: 'Resolved', type: 'success' })
                      } catch (err) {
                        toast.show({ message: getErrorMessage(err), type: 'error' })
                      }
                    }}>Resolve</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  )
}
