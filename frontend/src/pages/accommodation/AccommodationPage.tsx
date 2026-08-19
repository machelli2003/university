import { useState } from "react"
import { Link } from "react-router-dom"
import { AppShell } from "@/components/layout/AppShell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Select } from "@/components/ui/Select"
import { Input } from "@/components/ui/Input"
import { Badge } from "@/components/ui/Badge"
import { ErrorAlert, SuccessAlert, Spinner } from "@/components/ui/Feedback"
import {
  useHalls,
  useRooms,
  useReportMaintenance,
  useMyHousing,
  useSelectHousing,
} from "@/hooks/useAccommodation"
import { financeApi } from "@/services/api/finance"
import { getErrorMessage } from "@/services/api/client"
import { Building2, Home, Key, ShieldAlert, CheckCircle2, CreditCard, Sparkles } from "lucide-react"

type HousingTab = "school_hostel" | "outside_hostel" | "private_renting"

export default function AccommodationPage() {
  const { data: housingStatus, isLoading: housingLoading, refetch: refetchHousing } = useMyHousing()
  const { data: halls } = useHalls()
  const [selectedHall, setSelectedHall] = useState("")
  const { data: rooms, isLoading: roomsLoading } = useRooms(selectedHall)

  const selectHousingMutation = useSelectHousing()
  const maintenanceMutation = useReportMaintenance()

  const [activeTab, setActiveTab] = useState<HousingTab>("school_hostel")
  const [issueText, setIssueText] = useState("")

  const [isPayingHostelFee, setIsPayingHostelFee] = useState(false)
  const [isPayingSchoolFee, setIsPayingSchoolFee] = useState(false)
  const [paymentSuccessMsg, setPaymentSuccessMsg] = useState<string | null>(null)

  // Form states for Outside Hostel
  const [outsideHostelName, setOutsideHostelName] = useState("")
  const [outsideHostelAddress, setOutsideHostelAddress] = useState("")
  const [outsideHostelContact, setOutsideHostelContact] = useState("")

  // Form states for Private Renting
  const [privateAddress, setPrivateAddress] = useState("")
  const [privateCity, setPrivateCity] = useState("")
  const [privateContact, setPrivateContact] = useState("")

  const schoolFeePaid = housingStatus?.school_fee_paid ?? false
  const hostelFeePaid = housingStatus?.hostel_fee_paid ?? false

  const handlePayHostelFeeWithPaystack = async () => {
    if (!housingStatus?.student_id) return
    setIsPayingHostelFee(true)
    setPaymentSuccessMsg(null)
    try {
      const res = await financeApi.initiatePayment({
        student_id: housingStatus.student_id,
        amount: 1000.0,
        fee_type: "hostel",
        payment_method: "card",
      })

      if (res.authorization_url && !res.authorization_url.includes("sandbox-")) {
        window.open(res.authorization_url, "_blank")
      }

      await financeApi.verifyPayment(res.payment_reference)
      setPaymentSuccessMsg("Hostel Fee of GHS 1,000.00 successfully paid via Paystack! Room booking is now unlocked.")
      refetchHousing()
    } catch (err: any) {
      alert(err?.response?.data?.detail || err?.message || "Failed to process Paystack payment.")
    } finally {
      setIsPayingHostelFee(false)
    }
  }

  const handlePaySchoolFeeWithPaystack = async () => {
    if (!housingStatus?.student_id) return
    setIsPayingSchoolFee(true)
    setPaymentSuccessMsg(null)
    try {
      const res = await financeApi.initiatePayment({
        student_id: housingStatus.student_id,
        amount: 2500.0,
        fee_type: "tuition",
        payment_method: "card",
      })

      if (res.authorization_url && !res.authorization_url.includes("sandbox-")) {
        window.open(res.authorization_url, "_blank")
      }

      await financeApi.verifyPayment(res.payment_reference)
      setPaymentSuccessMsg("School Fees successfully cleared via Paystack! Housing registration is now unlocked.")
      refetchHousing()
    } catch (err: any) {
      alert(err?.response?.data?.detail || err?.message || "Failed to process Paystack payment.")
    } finally {
      setIsPayingSchoolFee(false)
    }
  }

  const handleSelectSchoolHostelRoom = (roomId: string) => {
    if (!selectedHall || !roomId) return
    selectHousingMutation.mutate(
      {
        housing_type: "school_hostel",
        hall_id: selectedHall,
        room_id: roomId,
      },
      {
        onSuccess: () => refetchHousing(),
      }
    )
  }

  const handleSelectOutsideHostel = (e: React.FormEvent) => {
    e.preventDefault()
    selectHousingMutation.mutate(
      {
        housing_type: "outside_hostel",
        outside_hostel_name: outsideHostelName,
        outside_hostel_address: outsideHostelAddress,
        outside_hostel_contact: outsideHostelContact,
      },
      {
        onSuccess: () => refetchHousing(),
      }
    )
  }

  const handleSelectPrivateRenting = (e: React.FormEvent) => {
    e.preventDefault()
    selectHousingMutation.mutate(
      {
        housing_type: "private_renting",
        private_address: privateAddress,
        private_city: privateCity,
        private_contact: privateContact,
      },
      {
        onSuccess: () => refetchHousing(),
      }
    )
  }

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink mb-1">Accommodation Portal</h1>
          <p className="text-cocoa-400">
            Manage your student housing status, pay hostel fees (GHS 1,000.00 via Paystack), book university hostels, or register off-campus accommodation.
          </p>
        </div>

        {paymentSuccessMsg && (
          <div className="mb-4">
            <SuccessAlert message={paymentSuccessMsg} />
          </div>
        )}

        {housingLoading ? (
          <div className="flex items-center justify-center p-8">
            <Spinner />
          </div>
        ) : (
          <>
            {/* Status & Fee Clearance Card */}
            <Card className="border-l-4 border-l-cocoa-600 shadow-sm">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <Building2 className="h-5 w-5 text-cocoa-600" />
                    Current Housing &amp; Fee Status
                  </CardTitle>
                  <Badge variant={housingStatus?.housing_status !== "unassigned" ? "success" : "warning"}>
                    {housingStatus?.housing_status === "school_hostel"
                      ? "On-Campus Hostel"
                      : housingStatus?.housing_status === "outside_hostel"
                      ? "Outside Hostel"
                      : housingStatus?.housing_status === "private_renting"
                      ? "Private Renting"
                      : "Housing Unassigned"}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {/* School Fees Status */}
                  <div className="rounded-lg border border-cocoa-100 p-4 bg-cocoa-50/50">
                    <p className="text-xs font-semibold text-cocoa-400 uppercase tracking-wider mb-1">
                      School Fees Clearance
                    </p>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {schoolFeePaid ? (
                          <>
                            <CheckCircle2 className="h-5 w-5 text-green-600" />
                            <span className="font-medium text-green-700">Fees Cleared</span>
                          </>
                        ) : (
                          <>
                            <ShieldAlert className="h-5 w-5 text-red-600" />
                            <span className="font-medium text-red-700">Unpaid / Outstanding</span>
                          </>
                        )}
                      </div>
                      {!schoolFeePaid && (
                        <Button
                          size="sm"
                          variant="outline"
                          isLoading={isPayingSchoolFee}
                          onClick={handlePaySchoolFeeWithPaystack}
                          className="text-xs border-red-300 text-red-700 hover:bg-red-50"
                        >
                          Pay via Paystack
                        </Button>
                      )}
                    </div>
                  </div>

                  {/* Hostel Fee Status */}
                  <div className="rounded-lg border border-cocoa-100 p-4 bg-cocoa-50/50">
                    <p className="text-xs font-semibold text-cocoa-400 uppercase tracking-wider mb-1">
                      Hostel Fee Status (GHS 1,000.00)
                    </p>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {hostelFeePaid ? (
                          <>
                            <CheckCircle2 className="h-5 w-5 text-green-600" />
                            <span className="font-medium text-green-700">Paid (GHS 1,000.00)</span>
                          </>
                        ) : (
                          <>
                            <ShieldAlert className="h-5 w-5 text-amber-600" />
                            <span className="font-medium text-amber-700">GHS 1,000.00 Due</span>
                          </>
                        )}
                      </div>
                      {!hostelFeePaid && schoolFeePaid && (
                        <Button
                          size="sm"
                          isLoading={isPayingHostelFee}
                          onClick={handlePayHostelFeeWithPaystack}
                          className="text-xs bg-emerald-600 hover:bg-emerald-700 text-white"
                        >
                          <CreditCard className="h-3.5 w-3.5 mr-1" />
                          Pay GHS 1,000
                        </Button>
                      )}
                    </div>
                  </div>

                  {/* Assigned Location */}
                  <div className="rounded-lg border border-cocoa-100 p-4 bg-cocoa-50/50">
                    <p className="text-xs font-semibold text-cocoa-400 uppercase tracking-wider mb-1">
                      Assigned Location
                    </p>
                    {housingStatus?.housing_status === "school_hostel" ? (
                      <p className="text-sm font-medium text-ink">
                        {housingStatus.hall_name || "Hall"} — Room {housingStatus.room_number || "—"}
                      </p>
                    ) : housingStatus?.housing_status === "outside_hostel" ? (
                      <p className="text-sm font-medium text-ink">
                        {housingStatus.outside_hostel_name || "Outside Hostel"}
                      </p>
                    ) : housingStatus?.housing_status === "private_renting" ? (
                      <p className="text-sm font-medium text-ink">
                        {housingStatus.private_address || "Private Rental"} ({housingStatus.private_city || "Off-Campus"})
                      </p>
                    ) : (
                      <p className="text-sm text-cocoa-400 italic">No housing registered yet</p>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* School Fee Gate Banner */}
            {!schoolFeePaid && (
              <div className="rounded-xl border border-red-200 bg-red-50 p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-start gap-3">
                  <ShieldAlert className="h-6 w-6 text-red-600 shrink-0 mt-0.5" />
                  <div>
                    <h3 className="font-semibold text-red-800">School Fees Payment Required</h3>
                    <p className="text-sm text-red-700">
                      As a newly admitted student, you must pay your school fees before you can book university hostels or register off-campus housing.
                    </p>
                  </div>
                </div>
                <Button
                  isLoading={isPayingSchoolFee}
                  onClick={handlePaySchoolFeeWithPaystack}
                  className="bg-red-600 hover:bg-red-700 text-white whitespace-nowrap"
                >
                  <CreditCard className="h-4 w-4 mr-2" />
                  Pay School Fees via Paystack
                </Button>
              </div>
            )}

            {/* Housing Options & Selection Forms */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Select Housing Option</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {selectHousingMutation.isError && (
                      <div className="mb-4"><ErrorAlert message={getErrorMessage(selectHousingMutation.error)} /></div>
                    )}
                    {selectHousingMutation.isSuccess && (
                      <div className="mb-4"><SuccessAlert message="Housing choice saved successfully!" /></div>
                    )}

                    {/* Choice Tabs */}
                    <div className="flex border-b border-cocoa-100 mb-6 gap-2">
                      <button
                        type="button"
                        onClick={() => setActiveTab("school_hostel")}
                        className={`flex items-center gap-2 pb-3 px-4 text-sm font-medium border-b-2 transition-colors ${
                          activeTab === "school_hostel"
                            ? "border-cocoa-900 text-cocoa-900 font-semibold"
                            : "border-transparent text-cocoa-500 hover:text-cocoa-700"
                        }`}
                      >
                        <Building2 className="h-4 w-4" />
                        School Hostel (GHS 1,000)
                      </button>

                      <button
                        type="button"
                        onClick={() => setActiveTab("outside_hostel")}
                        className={`flex items-center gap-2 pb-3 px-4 text-sm font-medium border-b-2 transition-colors ${
                          activeTab === "outside_hostel"
                            ? "border-cocoa-900 text-cocoa-900 font-semibold"
                            : "border-transparent text-cocoa-500 hover:text-cocoa-700"
                        }`}
                      >
                        <Home className="h-4 w-4" />
                        Outside Hostel
                      </button>

                      <button
                        type="button"
                        onClick={() => setActiveTab("private_renting")}
                        className={`flex items-center gap-2 pb-3 px-4 text-sm font-medium border-b-2 transition-colors ${
                          activeTab === "private_renting"
                            ? "border-cocoa-900 text-cocoa-900 font-semibold"
                            : "border-transparent text-cocoa-500 hover:text-cocoa-700"
                        }`}
                      >
                        <Key className="h-4 w-4" />
                        Private Renting
                      </button>
                    </div>

                    {/* TAB 1: SCHOOL HOSTEL */}
                    {activeTab === "school_hostel" && (
                      <div className="space-y-4">
                        {!hostelFeePaid ? (
                          <div className="rounded-xl border border-amber-200 bg-amber-50 p-5">
                            <div className="flex items-start justify-between gap-4">
                              <div>
                                <h4 className="font-semibold text-amber-900 text-base mb-1">
                                  Hostel Fee: GHS 1,000.00 Required
                                </h4>
                                <p className="text-sm text-amber-800 mb-4">
                                  To book an on-campus hostel room, please pay the university hostel fee of GHS 1,000.00 using Paystack (Mobile Money / Bank Card).
                                </p>
                              </div>
                              <Sparkles className="h-8 w-8 text-amber-600 shrink-0" />
                            </div>
                            <Button
                              isLoading={isPayingHostelFee}
                              disabled={!schoolFeePaid}
                              onClick={handlePayHostelFeeWithPaystack}
                              className="bg-emerald-600 hover:bg-emerald-700 text-white font-medium"
                            >
                              <CreditCard className="h-4 w-4 mr-2" />
                              Pay GHS 1,000.00 via Paystack
                            </Button>
                          </div>
                        ) : (
                          <>
                            <div className="flex items-center gap-2 rounded-lg bg-green-50 border border-green-200 p-3 text-sm text-green-800 mb-3">
                              <CheckCircle2 className="h-5 w-5 text-green-600 shrink-0" />
                              <span>Hostel Fee of GHS 1,000.00 has been verified! Choose your preferred hall and room below.</span>
                            </div>

                            <Select
                              label="Select Hall of Residence"
                              value={selectedHall}
                              onChange={(e) => setSelectedHall(e.target.value)}
                              disabled={!schoolFeePaid}
                            >
                              <option value="">Choose a hall...</option>
                              {halls?.map((h) => (
                                <option key={h.id} value={h.id}>
                                  {h.name} (Capacity: {h.capacity})
                                </option>
                              ))}
                            </Select>

                            {roomsLoading && <Spinner />}

                            {selectedHall && rooms && (
                              <div className="space-y-2 mt-4">
                                <p className="text-sm font-medium text-ink">Available Rooms in Selected Hall</p>
                                {rooms.map((room) => (
                                  <div
                                    key={room.id}
                                    className="flex items-center justify-between border border-cocoa-100 rounded-lg px-4 py-3 bg-white hover:border-cocoa-300 transition-colors"
                                  >
                                    <div>
                                      <p className="font-medium text-sm text-ink">Room {room.room_number}</p>
                                      <p className="text-xs text-cocoa-400 capitalize">
                                        Type: {room.room_type} — {room.occupied}/{room.capacity} Occupied
                                      </p>
                                    </div>
                                    <Button
                                      size="sm"
                                      disabled={room.occupied >= room.capacity || !schoolFeePaid || selectHousingMutation.isPending}
                                      isLoading={selectHousingMutation.isPending}
                                      onClick={() => handleSelectSchoolHostelRoom(room.id)}
                                    >
                                      {room.occupied >= room.capacity ? "Full" : "Book Room"}
                                    </Button>
                                  </div>
                                ))}
                              </div>
                            )}
                          </>
                        )}
                      </div>
                    )}

                    {/* TAB 2: OUTSIDE HOSTEL */}
                    {activeTab === "outside_hostel" && (
                      <form onSubmit={handleSelectOutsideHostel} className="space-y-4">
                        <p className="text-sm text-cocoa-500">
                          No university hostel fee required. Register your details if you are staying in an accredited or private off-campus hostel.
                        </p>

                        <Input
                          label="Outside Hostel Name"
                          placeholder="e.g. Royal Plaza Hostel"
                          value={outsideHostelName}
                          onChange={(e) => setOutsideHostelName(e.target.value)}
                          required
                          disabled={!schoolFeePaid}
                        />

                        <Input
                          label="Hostel Address / Location"
                          placeholder="e.g. 15 University Avenue, South Campus"
                          value={outsideHostelAddress}
                          onChange={(e) => setOutsideHostelAddress(e.target.value)}
                          disabled={!schoolFeePaid}
                        />

                        <Input
                          label="Hostel Manager / Contact Person Phone"
                          placeholder="e.g. +233 24 000 0000"
                          value={outsideHostelContact}
                          onChange={(e) => setOutsideHostelContact(e.target.value)}
                          required
                          disabled={!schoolFeePaid}
                        />

                        <Button
                          type="submit"
                          disabled={!schoolFeePaid || !outsideHostelName || !outsideHostelContact}
                          isLoading={selectHousingMutation.isPending}
                        >
                          Register Outside Hostel
                        </Button>
                      </form>
                    )}

                    {/* TAB 3: PRIVATE RENTING */}
                    {activeTab === "private_renting" && (
                      <form onSubmit={handleSelectPrivateRenting} className="space-y-4">
                        <p className="text-sm text-cocoa-500">
                          No university hostel fee required. Register your residential details if you rent a private apartment or commute from home.
                        </p>

                        <Input
                          label="Residential / Apartment Address"
                          placeholder="e.g. House No. 42, Block C, Legon Road"
                          value={privateAddress}
                          onChange={(e) => setPrivateAddress(e.target.value)}
                          required
                          disabled={!schoolFeePaid}
                        />

                        <Input
                          label="City / Town / Area"
                          placeholder="e.g. Accra"
                          value={privateCity}
                          onChange={(e) => setPrivateCity(e.target.value)}
                          disabled={!schoolFeePaid}
                        />

                        <Input
                          label="Landlord or Emergency Contact Phone"
                          placeholder="e.g. +233 50 111 2222"
                          value={privateContact}
                          onChange={(e) => setPrivateContact(e.target.value)}
                          required
                          disabled={!schoolFeePaid}
                        />

                        <Button
                          type="submit"
                          disabled={!schoolFeePaid || !privateAddress || !privateContact}
                          isLoading={selectHousingMutation.isPending}
                        >
                          Register Rental Location
                        </Button>
                      </form>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* Maintenance Reporting Column */}
              <div>
                <Card>
                  <CardHeader>
                    <CardTitle>Report Maintenance Issue</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {maintenanceMutation.isError && (
                      <div className="mb-4"><ErrorAlert message={getErrorMessage(maintenanceMutation.error)} /></div>
                    )}
                    {maintenanceMutation.isSuccess && (
                      <div className="mb-4"><SuccessAlert message="Maintenance request submitted successfully." /></div>
                    )}

                    <div className="space-y-4">
                      <Select
                        label="Hall"
                        value={selectedHall}
                        onChange={(e) => setSelectedHall(e.target.value)}
                      >
                        <option value="">Choose a hall...</option>
                        {halls?.map((h) => (
                          <option key={h.id} value={h.id}>
                            {h.name}
                          </option>
                        ))}
                      </Select>

                      <Input
                        label="Describe the issue"
                        placeholder="e.g. Broken window latch, leaking pipe"
                        value={issueText}
                        onChange={(e) => setIssueText(e.target.value)}
                      />

                      <Button
                        className="w-full"
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
            </div>
          </>
        )}
      </div>
    </AppShell>
  )
}


