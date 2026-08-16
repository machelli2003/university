import { useState } from "react"
import { AppShell } from "@/components/layout/AppShell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Link } from "react-router-dom"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { adminApi } from "@/services/api/admin"
import { getErrorMessage } from "@/services/api/client"
import { useAuthStore } from "@/store/authStore"
import {
  Users,
  BarChart3,
  Wallet,
  BookOpen,
  Building2,
  Briefcase,
  HeartPulse,
  FlaskConical,
  GraduationCap as AlumniIcon,
  Bell,
  FileCheck,
  FileText,
  GitBranch,
  Boxes,
  Settings,
  ShieldCheck,
  Plus,
} from "lucide-react"

const ADMIN_MODULES = [
  { label: "Analytics", path: "/analytics", icon: <BarChart3 className="h-5 w-5" /> },
  { label: "User Management", path: "/admin/users", icon: <Users className="h-5 w-5" /> },
  { label: "University Settings", path: "/admin/university-settings", icon: <Settings className="h-5 w-5" /> },
  { label: "All Applicants", path: "/officer/applicants", icon: <Users className="h-5 w-5" /> },
  { label: "Payments", path: "/finance/payments", icon: <Wallet className="h-5 w-5" /> },
  { label: "Library", path: "/library", icon: <BookOpen className="h-5 w-5" /> },
  { label: "Accommodation", path: "/accommodation", icon: <Building2 className="h-5 w-5" /> },
  { label: "HR — Approve Leaves", path: "/hr/approve-leaves", icon: <Briefcase className="h-5 w-5" /> },
  { label: "Health Services", path: "/health", icon: <HeartPulse className="h-5 w-5" /> },
  { label: "Research", path: "/research", icon: <FlaskConical className="h-5 w-5" /> },
  { label: "Alumni", path: "/alumni", icon: <AlumniIcon className="h-5 w-5" /> },
  { label: "Campaigns", path: "/communication/campaigns", icon: <Bell className="h-5 w-5" /> },
  { label: "Documents", path: "/documents", icon: <FileText className="h-5 w-5" /> },
  { label: "Approval Tasks", path: "/workflow/tasks", icon: <GitBranch className="h-5 w-5" /> },
  { label: "Inventory", path: "/inventory", icon: <Boxes className="h-5 w-5" /> },
  { label: "Registrar", path: "/registrar", icon: <Users className="h-5 w-5" /> },
  { label: "Head of Department", path: "/head-of-department", icon: <Settings className="h-5 w-5" /> },
  { label: "Dean", path: "/dean", icon: <ShieldCheck className="h-5 w-5" /> },
  { label: "Finance Officer", path: "/finance/officer", icon: <Wallet className="h-5 w-5" /> },
  { label: "Applications", path: "/admin/university-applications", icon: <FileCheck className="h-5 w-5" /> },
  { label: "Auditor", path: "/auditor", icon: <FileText className="h-5 w-5" /> },
]

export default function AdminDashboardPage() {
  const user = useAuthStore((s) => s.user)
  const [adminForm, setAdminForm] = useState({
    email: "",
    first_name: "",
    last_name: "",
    password: "",
  })
  const [adminCreateError, setAdminCreateError] = useState<string | null>(null)
  const [adminCreateSuccess, setAdminCreateSuccess] = useState<string | null>(null)
  const [adminCreating, setAdminCreating] = useState(false)

  const handleCreateUniversityAdmin = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setAdminCreateError(null)
    setAdminCreateSuccess(null)

    try {
      setAdminCreating(true)
      const password = adminForm.password || "UniversityAdmin@2026"
      const tenantId = user?.tenant_id || "single-university"

      await adminApi.createUser({
        email: adminForm.email,
        first_name: adminForm.first_name,
        last_name: adminForm.last_name,
        password,
        role: "university_admin",
        tenant_id: tenantId,
        must_change_password: true,
      })

      setAdminCreateSuccess(`University admin created for University of Machelli. Default password: ${password}. They must change it on first login.`)
      setAdminForm({ email: "", first_name: "", last_name: "", password: "" })
    } catch (err) {
      setAdminCreateError(getErrorMessage(err))
    } finally {
      setAdminCreating(false)
    }
  }

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink mb-1">University of Machelli</h1>
          <p className="text-cocoa-400 mb-6">Single-university administration dashboard.</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Create University Admin</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCreateUniversityAdmin} className="space-y-4">
              <Input label="University Admin Email" type="email" value={adminForm.email} onChange={(e) => setAdminForm({ ...adminForm, email: e.target.value })} required />
              <div className="grid gap-4 sm:grid-cols-2">
                <Input label="First Name" value={adminForm.first_name} onChange={(e) => setAdminForm({ ...adminForm, first_name: e.target.value })} required />
                <Input label="Last Name" value={adminForm.last_name} onChange={(e) => setAdminForm({ ...adminForm, last_name: e.target.value })} required />
              </div>
              <Input label="Default Password" type="text" value={adminForm.password} onChange={(e) => setAdminForm({ ...adminForm, password: e.target.value })} placeholder="Leave blank to use UniversityAdmin@2026" />
              {adminCreateError && <p className="text-sm text-red-600">{adminCreateError}</p>}
              {adminCreateSuccess && <p className="text-sm text-green-600">{adminCreateSuccess}</p>}
              <Button type="submit" isLoading={adminCreating} className="inline-flex items-center gap-2">
                <Plus className="h-4 w-4" />
                Create University Admin
              </Button>
            </form>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {ADMIN_MODULES.map((mod) => (
            <Link key={mod.path} to={mod.path}>
              <Card className="hover:border-cocoa-300 transition-colors cursor-pointer h-full">
                <CardContent className="flex items-center gap-3 py-5">
                  <span className="flex h-10 w-10 items-center justify-center rounded-md bg-cocoa-50 text-cocoa-600">
                    {mod.icon}
                  </span>
                  <span className="font-medium text-sm text-ink">{mod.label}</span>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </div>
    </AppShell>
  )
}
