import { AppShell } from "@/components/layout/AppShell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"

export default function AlumniPortalPage() {
  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink mb-1">Alumni Portal</h1>
          <p className="text-cocoa-400">Build your alumni network, mentor students, and support the university community.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader><CardTitle>Directory</CardTitle></CardHeader>
            <CardContent>
              <p className="text-sm text-cocoa-500 mb-4">Browse graduates and alumni professionals across industries.</p>
              <Button variant="outline" onClick={() => window.location.href = "/alumni"}>Open directory</Button>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Mentorship</CardTitle></CardHeader>
            <CardContent>
              <p className="text-sm text-cocoa-500 mb-4">Offer guidance, career advice, and internship referrals.</p>
              <Button variant="outline" onClick={() => window.location.href = "/alumni"}>Request mentorship</Button>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Giving</CardTitle></CardHeader>
            <CardContent>
              <p className="text-sm text-cocoa-500 mb-4">Fund scholarships, facilities, and student support programmes.</p>
              <Button variant="outline" onClick={() => window.location.href = "/alumni"}>Support alumni fund</Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppShell>
  )
}
