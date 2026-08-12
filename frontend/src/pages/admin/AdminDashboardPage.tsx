import { AppShell } from "@/components/layout/AppShell"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Link } from "react-router-dom"
import { Button } from "@/components/ui/Button"
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
  FileText,
  GitBranch,
  Boxes,
  Settings,
  ShieldCheck,
} from "lucide-react"

const ADMIN_MODULES = [
  { label: "Analytics", path: "/analytics", icon: <BarChart3 className="h-5 w-5" /> },
  { label: "User Management", path: "/admin/users", icon: <Users className="h-5 w-5" /> },
  { label: "Tenant Settings", path: "/admin/tenant-settings", icon: <Settings className="h-5 w-5" /> },
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
  { label: "Super Admin", path: "/super-admin", icon: <ShieldCheck className="h-5 w-5" /> },
  { label: "Auditor", path: "/auditor", icon: <FileText className="h-5 w-5" /> },
]

export default function AdminDashboardPage() {
  return (
    <AppShell>
      <h1 className="font-display text-2xl font-semibold text-ink mb-1">Admin Dashboard</h1>
      <p className="text-cocoa-400 mb-6">Quick access to every module across the platform.</p>

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
    </AppShell>
  )
}
