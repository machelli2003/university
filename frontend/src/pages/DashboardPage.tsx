import { useAuthStore } from "@/store/authStore"
import { AppShell } from "@/components/layout/AppShell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Link } from "react-router-dom"
import { Button } from "@/components/ui/Button"

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user)

  const isOfficer = user && ["admissions_officer", "registrar", "university_admin", "super_admin"].includes(user.role)

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
