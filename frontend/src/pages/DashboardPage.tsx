import { useAuthStore } from "@/store/authStore"
import { AppShell } from "@/components/layout/AppShell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Link } from "react-router-dom"
import { Button } from "@/components/ui/Button"
import SuperAdminDashboardPage from "@/pages/officer/SuperAdminDashboardPage"

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user)

  if (user?.role === "super_admin") {
    return (
      <AppShell>
        <div className="space-y-6">
          <h1 className="font-display text-2xl font-semibold text-ink mb-1">University of Machelli</h1>
          <p className="text-cocoa-400 mb-6">Single-university administration dashboard.</p>
          <SuperAdminDashboardPage />
        </div>
      </AppShell>
    )
  }

  if (user?.role === "student") {
    return (
      <AppShell>
        <div className="space-y-6">
          <h1 className="font-display text-2xl font-semibold text-ink mb-1">Student Workspace</h1>
          <p className="text-cocoa-400 mb-6">Manage your academic record, fees, timetable, and registration.</p>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
            <Card>
              <CardHeader><CardTitle>Student Portal</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-cocoa-500 mb-4">Review your academic progress, record, and results.</p>
                <Link to="/student"><Button>Open dashboard</Button></Link>
              </CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle>Course Registration</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-cocoa-500 mb-4">Select semester courses and submit registration.</p>
                <Link to="/academic/registration"><Button>Register now</Button></Link>
              </CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle>Fees & Payments</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-cocoa-500 mb-4">Track balances, invoices, and payment status.</p>
                <Link to="/finance/payments"><Button>View fees</Button></Link>
              </CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle>Results</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-cocoa-500 mb-4">Review grades, transcripts, and performance history.</p>
                <Link to="/student/results"><Button>Open results</Button></Link>
              </CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle>Timetable</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-cocoa-500 mb-4">View your weekly lecture and lab schedule.</p>
                <Link to="/student/timetable"><Button>Open timetable</Button></Link>
              </CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle>Alumni Network</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-cocoa-500 mb-4">Connect with alumni mentors and support the community.</p>
                <Link to="/alumni"><Button>Open alumni</Button></Link>
              </CardContent>
            </Card>
          </div>
        </div>
      </AppShell>
    )
  }

  if (user?.role === "lecturer") {
    return (
      <AppShell>
        <div className="space-y-6">
          <h1 className="font-display text-2xl font-semibold text-ink mb-1">Lecturer Workspace</h1>
          <p className="text-cocoa-400 mb-6">Manage your courses, attendance, grading, and materials.</p>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
            <Card>
              <CardHeader><CardTitle>My Courses</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-cocoa-500 mb-4">Open your teaching schedule and assigned classes.</p>
                <Link to="/officer/dashboard/lecturer"><Button>Open dashboard</Button></Link>
              </CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle>Attendance</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-cocoa-500 mb-4">Track class attendance and export reports.</p>
                <Link to="/lecturer/attendance"><Button>Open roster</Button></Link>
              </CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle>Grades</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-cocoa-500 mb-4">Submit and review marks for enrolled students.</p>
                <Link to="/exam/submit-grades"><Button>Submit grades</Button></Link>
              </CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle>Materials</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-cocoa-500 mb-4">Upload lecture notes, resources, and files.</p>
                <Link to="/lecturer"><Button>Course library</Button></Link>
              </CardContent>
            </Card>
          </div>
        </div>
      </AppShell>
    )
  }

  if (user?.role === "head_of_department") {
    return (
      <AppShell>
        <div className="space-y-6">
          <h1 className="font-display text-2xl font-semibold text-ink mb-1">Head of Department Workspace</h1>
          <p className="text-cocoa-400 mb-6">Review department outcomes, staffing, and academic quality.</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader><CardTitle>Department Overview</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-cocoa-500 mb-4">Monitor courses, lecturers, and student loads.</p>
                <Link to="/officer/dashboard/hod"><Button>Open dashboard</Button></Link>
              </CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle>Grade Approval</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-cocoa-500 mb-4">Review and approve marks before faculty submission.</p>
                <Link to="/exam/approve-grades"><Button>Review approvals</Button></Link>
              </CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle>Leave Approvals</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-cocoa-500 mb-4">Approve or track staff leave requests.</p>
                <Link to="/hr/approve-leaves"><Button>View requests</Button></Link>
              </CardContent>
            </Card>
          </div>
        </div>
      </AppShell>
    )
  }

  if (user?.role === "dean") {
    return (
      <AppShell>
        <div className="space-y-6">
          <h1 className="font-display text-2xl font-semibold text-ink mb-1">Dean Workspace</h1>
          <p className="text-cocoa-400 mb-6">Manage faculty performance, programmes, and strategic oversight.</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader><CardTitle>Faculty Dashboard</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-cocoa-500 mb-4">Track departments, programmes, and student population.</p>
                <Link to="/officer/dashboard/dean"><Button>Open faculty dashboard</Button></Link>
              </CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle>Grade Oversight</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-cocoa-500 mb-4">Review marks and approval cycles across faculties.</p>
                <Link to="/exam/approve-grades"><Button>Open approvals</Button></Link>
              </CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle>Academic Strategy</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-cocoa-500 mb-4">Oversee curriculum quality and department performance.</p>
                <Link to="/dean"><Button>Faculty overview</Button></Link>
              </CardContent>
            </Card>
          </div>
        </div>
      </AppShell>
    )
  }

  if (user?.role === "registrar") {
    return (
      <AppShell>
        <div className="space-y-6">
          <h1 className="font-display text-2xl font-semibold text-ink mb-1">Registrar Workspace</h1>
          <p className="text-cocoa-400 mb-6">Drive enrollment, academic standing, and student records.</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader><CardTitle>Enrollment Dashboard</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-cocoa-500 mb-4">Review student enrolment quality and progression metrics.</p>
                <Link to="/officer/dashboard/registrar"><Button>Open dashboard</Button></Link>
              </CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle>Applicants</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-cocoa-500 mb-4">Manage admissions records and student flow.</p>
                <Link to="/officer/applicants"><Button>View applicants</Button></Link>
              </CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle>Academic Records</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-cocoa-500 mb-4">Track transcripts, standing, and progression decisions.</p>
                <Link to="/registrar"><Button>Open records</Button></Link>
              </CardContent>
            </Card>
          </div>
        </div>
      </AppShell>
    )
  }

  if (user?.role === "finance_officer") {
    return (
      <AppShell>
        <div className="space-y-6">
          <h1 className="font-display text-2xl font-semibold text-ink mb-1">Finance Workspace</h1>
          <p className="text-cocoa-400 mb-6">Monitor fee collection, payments, and financial reconciliation.</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader><CardTitle>Finance Dashboard</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-cocoa-500 mb-4">Track revenue, outstanding balances, and payment health.</p>
                <Link to="/officer/dashboard/finance"><Button>Open dashboard</Button></Link>
              </CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle>Payments</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-cocoa-500 mb-4">Confirm, reject, and reconcile student payments.</p>
                <Link to="/finance/payments"><Button>Manage payments</Button></Link>
              </CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle>Fee Structures</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-cocoa-500 mb-4">Review fee policy and scholarship configuration.</p>
                <Link to="/finance/officer"><Button>Open finance hub</Button></Link>
              </CardContent>
            </Card>
          </div>
        </div>
      </AppShell>
    )
  }

  if (user?.role === "hostel_administrator") {
    return (
      <AppShell>
        <div className="space-y-6">
          <h1 className="font-display text-2xl font-semibold text-ink mb-1">Hostel Workspace</h1>
          <p className="text-cocoa-400 mb-6">Manage occupancy, accommodations, and maintenance oversight.</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader><CardTitle>Occupancy Dashboard</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-cocoa-500 mb-4">Track hostel occupancy and room utilization.</p>
                <Link to="/officer/dashboard/hostel"><Button>Open dashboard</Button></Link>
              </CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle>Rooms & Beds</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-cocoa-500 mb-4">Review room allocations and student assignment history.</p>
                <Link to="/hostel"><Button>Manage accommodation</Button></Link>
              </CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle>Maintenance</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-cocoa-500 mb-4">Handle maintenance issues and room readiness.</p>
                <Link to="/hostel"><Button>View requests</Button></Link>
              </CardContent>
            </Card>
          </div>
        </div>
      </AppShell>
    )
  }

  if (user?.role === "librarian") {
    return (
      <AppShell>
        <div className="space-y-6">
          <h1 className="font-display text-2xl font-semibold text-ink mb-1">Library Workspace</h1>
          <p className="text-cocoa-400 mb-6">Manage inventory, issue logs, and member borrowing activity.</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader><CardTitle>Library Dashboard</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-cocoa-500 mb-4">Track books, checkouts, availability, and overdue items.</p>
                <Link to="/officer/dashboard/librarian"><Button>Open dashboard</Button></Link>
              </CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle>Catalog</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-cocoa-500 mb-4">Add books and search the collection for borrowing.</p>
                <Link to="/librarian"><Button>Manage library</Button></Link>
              </CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle>Borrowing</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-cocoa-500 mb-4">Monitor returns and overdue borrowings across the library.</p>
                <Link to="/officer/dashboard/librarian"><Button>Review activity</Button></Link>
              </CardContent>
            </Card>
          </div>
        </div>
      </AppShell>
    )
  }

  if (user?.role === "examination_officer") {
    return (
      <AppShell>
        <div className="space-y-6">
          <h1 className="font-display text-2xl font-semibold text-ink mb-1">Examination Workspace</h1>
          <p className="text-cocoa-400 mb-6">Coordinate exam schedules, results, and verification tracking.</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader><CardTitle>Exam Dashboard</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-cocoa-500 mb-4">Monitor exams and results verification status.</p>
                <Link to="/officer/dashboard/exam"><Button>Open dashboard</Button></Link>
              </CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle>Results</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-cocoa-500 mb-4">Review exam outputs and pending verification work.</p>
                <Link to="/officer/dashboard/exam"><Button>Review results</Button></Link>
              </CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle>Scheduling</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-cocoa-500 mb-4">Plan and manage exam calendar coordination.</p>
                <Link to="/officer/dashboard/exam"><Button>Open schedule</Button></Link>
              </CardContent>
            </Card>
          </div>
        </div>
      </AppShell>
    )
  }

  const isOfficer = user && ["admissions_officer", "registrar", "university_admin"].includes(user.role)

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-semibold text-ink mb-1">
        Welcome back, {user?.first_name}
      </h1>
      <p className="text-cocoa-400 mb-8 capitalize">{user?.role.replace(/_/g, " ")}</p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {!isOfficer && (
          <Card>
            <CardHeader>
              <CardTitle>Your Application</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-cocoa-500 mb-4">
                Track your admission application, submit results, and check your status.
              </p>
              <Link to="/apply/status">
                <Button>View Application</Button>
              </Link>
            </CardContent>
          </Card>
        )}

        {isOfficer && (
          <>
            <Card>
              <CardHeader>
                <CardTitle>Pending Results</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-cocoa-500 mb-4">
                  Review and approve manually submitted WASSCE/exam results.
                </p>
                <Link to="/officer/pending-results">
                  <Button>Review Results</Button>
                </Link>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Process Admissions</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-cocoa-500 mb-4">
                  Run eligibility checks, ranking, allocation, and publish offers.
                </p>
                <Link to="/officer/processing">
                  <Button>Open Processing</Button>
                </Link>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>All Applicants</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-cocoa-500 mb-4">
                  Browse and filter every application in the system.
                </p>
                <Link to="/officer/applicants">
                  <Button>View Applicants</Button>
                </Link>
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </AppShell>
  )
}
