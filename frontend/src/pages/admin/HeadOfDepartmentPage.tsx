import React from "react"
import { AppShell } from "@/components/layout/AppShell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { ProposalApprovalPanel } from "@/components/research/ProposalApprovalPanel"

export default function HeadOfDepartmentPage() {

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-semibold text-ink mb-1">Head of Department</h1>
      <p className="text-cocoa-400 mb-6">Coordinate department faculty, approve courses, and oversee academic quality.</p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <Card>
          <CardHeader>
            <CardTitle>Course Approval</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-cocoa-500">Review course proposals, assign instructors, and confirm department schedules.</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Faculty Coordination</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-cocoa-500">Manage teaching assignments, supervise academic staff, and support departmental planning.</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Student Reviews</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-cocoa-500">Monitor student progress, approve petitions, and support academic advising within the department.</p>
          </CardContent>
        </Card>
      </div>

      <ProposalApprovalPanel />
    </AppShell>
  )
}
