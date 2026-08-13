import { type ReactNode } from "react"
import { NavLink, useNavigate } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { useAuthStore } from "@/store/authStore"
import { useLogout } from "@/hooks/useAuth"
import { adminApi } from "@/services/api/admin"
import { tenantApi } from "@/services/api/tenant"
import { TenantSwitcher } from "@/components/ui/TenantSwitcher"
import { cn } from "@/lib/utils"
import {
  GraduationCap,
  LayoutDashboard,
  FileCheck,
  Users,
  Settings,
  LogOut,
  BookOpen,
  Wallet,
  ClipboardCheck,
  ClipboardList,
  Building2,
  Library as LibraryIcon,
  Briefcase,
  CalendarCheck,
  HeartPulse,
  FlaskConical,
  GraduationCap as AlumniIcon,
  Bell,
  Megaphone,
  FileText,
  GitBranch,
  Boxes,
  BarChart3,
  ShieldCheck,
} from "lucide-react"

interface NavItem {
  label: string
  path: string
  icon: ReactNode
  roles?: string[]
}

const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", path: "/dashboard", icon: <LayoutDashboard className="h-4 w-4" /> },

  // Applicant / student
  { label: "My Application", path: "/apply/status", icon: <FileCheck className="h-4 w-4" />, roles: ["applicant"] },
  { label: "Course Registration", path: "/academic/registration", icon: <BookOpen className="h-4 w-4" />, roles: ["student", "applicant"] },
  { label: "Payments", path: "/finance/payments", icon: <Wallet className="h-4 w-4" />, roles: ["student", "applicant", "finance_officer", "university_admin", "super_admin"] },
  { label: "Accommodation", path: "/accommodation", icon: <Building2 className="h-4 w-4" />, roles: ["student", "university_admin", "super_admin"] },
  { label: "Hostel Administration", path: "/hostel", icon: <Building2 className="h-4 w-4" />, roles: ["hostel_administrator", "university_admin", "super_admin"] },
  { label: "Library", path: "/library", icon: <LibraryIcon className="h-4 w-4" />, roles: ["student", "lecturer", "librarian", "university_admin", "super_admin"] },
  { label: "Librarian Tools", path: "/librarian", icon: <LibraryIcon className="h-4 w-4" />, roles: ["librarian", "university_admin", "super_admin"] },
  { label: "Counselor Inbox", path: "/counselor", icon: <HeartPulse className="h-4 w-4" />, roles: ["counselor", "university_admin", "super_admin"] },
  { label: "Parent Portal", path: "/parent", icon: <Users className="h-4 w-4" />, roles: ["parent_guardian", "university_admin", "super_admin"] },
  { label: "Health Services", path: "/health", icon: <HeartPulse className="h-4 w-4" />, roles: ["student", "applicant", "lecturer", "university_admin", "super_admin"] },
  { label: "Alumni", path: "/alumni", icon: <AlumniIcon className="h-4 w-4" />, roles: ["alumni", "university_admin", "super_admin"] },
  { label: "Documents", path: "/documents", icon: <FileText className="h-4 w-4" />, roles: ["student", "lecturer", "librarian", "university_admin", "super_admin"] },
  { label: "Notifications", path: "/communication/notifications", icon: <Bell className="h-4 w-4" />, roles: ["student", "applicant", "lecturer", "librarian", "hostel_administrator", "university_admin", "super_admin", "auditor", "finance_officer", "head_of_department", "dean"] },
  { label: "My Approval Tasks", path: "/workflow/tasks", icon: <GitBranch className="h-4 w-4" />, roles: ["admissions_officer", "registrar", "university_admin", "super_admin", "head_of_department", "dean"] },
  { label: "Request Leave", path: "/hr/request-leave", icon: <CalendarCheck className="h-4 w-4" />, roles: ["lecturer", "hostel_administrator", "head_of_department", "finance_officer", "university_admin", "super_admin"] },

  // Registrar / academic leadership
  { label: "Registrar", path: "/registrar", icon: <Users className="h-4 w-4" />, roles: ["registrar", "university_admin", "super_admin"] },
  { label: "Head of Department", path: "/head-of-department", icon: <Settings className="h-4 w-4" />, roles: ["head_of_department", "university_admin", "super_admin"] },
  { label: "Dean", path: "/dean", icon: <ShieldCheck className="h-4 w-4" />, roles: ["dean", "university_admin", "super_admin"] },
  { label: "Finance Officer", path: "/finance/officer", icon: <Wallet className="h-4 w-4" />, roles: ["finance_officer", "university_admin", "super_admin"] },
  { label: "Super Admin", path: "/super-admin", icon: <ShieldCheck className="h-4 w-4" />, roles: ["super_admin"] },
  { label: "Auditor", path: "/auditor", icon: <FileText className="h-4 w-4" />, roles: ["auditor", "university_admin", "super_admin"] },

  // Admissions officer
  {
    label: "Pending Results",
    path: "/officer/pending-results",
    icon: <FileCheck className="h-4 w-4" />,
    roles: ["admissions_officer", "registrar", "university_admin", "super_admin"],
  },
  {
    label: "All Applicants",
    path: "/officer/applicants",
    icon: <Users className="h-4 w-4" />,
    roles: ["admissions_officer", "registrar", "university_admin", "super_admin"],
  },
  {
    label: "Process Admissions",
    path: "/officer/processing",
    icon: <Settings className="h-4 w-4" />,
    roles: ["admissions_officer", "registrar", "university_admin", "super_admin"],
  },

  // Lecturer / grading
  {
    label: "My Courses",
    path: "/lecturer",
    icon: <BookOpen className="h-4 w-4" />,
    roles: ["lecturer"],
  },
  {
    label: "My Grades",
    path: "/exam/my-grades",
    icon: <ClipboardList className="h-4 w-4" />,
    roles: ["lecturer"],
  },
  {
    label: "Submit Grades",
    path: "/exam/submit-grades",
    icon: <ClipboardList className="h-4 w-4" />,
    roles: ["lecturer", "head_of_department", "dean"],
  },
  {
    label: "Approve Grades",
    path: "/exam/approve-grades",
    icon: <ClipboardCheck className="h-4 w-4" />,
    roles: ["head_of_department", "dean", "registrar"],
  },

  // HR approvers
  {
    label: "Approve Leaves",
    path: "/hr/approve-leaves",
    icon: <Briefcase className="h-4 w-4" />,
    roles: ["head_of_department", "university_admin", "super_admin"],
  },

  // Research
  {
    label: "Research",
    path: "/research",
    icon: <FlaskConical className="h-4 w-4" />,
    roles: ["lecturer", "dean", "head_of_department"],
  },

  // Comms admin
  {
    label: "Campaigns",
    path: "/communication/campaigns",
    icon: <Megaphone className="h-4 w-4" />,
    roles: ["university_admin", "super_admin", "registrar"],
  },

  // Admin-only
  {
    label: "Inventory",
    path: "/inventory",
    icon: <Boxes className="h-4 w-4" />,
    roles: ["university_admin", "super_admin"],
  },
  {
    label: "Analytics",
    path: "/analytics",
    icon: <BarChart3 className="h-4 w-4" />,
    roles: ["admissions_officer", "registrar", "finance_officer", "university_admin", "super_admin"],
  },
  {
    label: "Admin",
    path: "/admin",
    icon: <ShieldCheck className="h-4 w-4" />,
    roles: ["university_admin", "super_admin"],
  },
  {
    label: "Tenant Applications",
    path: "/admin/university-applications",
    icon: <FileCheck className="h-4 w-4" />,
    roles: ["super_admin", "university_admin"],
  },
  {
    label: "Tenant Settings",
    path: "/admin/tenant-settings",
    icon: <Settings className="h-4 w-4" />,
    roles: ["university_admin", "super_admin"],
  },
]

export function AppShell({ children }: { children: ReactNode }) {
  const user = useAuthStore((s) => s.user)
  const selectedTenantId = useAuthStore((s) => s.selectedTenantId)
  const setSelectedTenantId = useAuthStore((s) => s.setSelectedTenantId)
  const logout = useLogout()
  const navigate = useNavigate()

  const tenantQuery = useQuery({
    queryKey: ["tenants", "switcher"],
    queryFn: () => tenantApi.listTenants(true),
    enabled: user?.role === "super_admin",
    staleTime: 1000 * 60 * 5,
  })

  const visibleItems = NAV_ITEMS.filter((item) => {
    // If item has no role restriction, it's public
    if (!item.roles) return true

    // If current user is super_admin and hasn't selected a tenant,
    // only show items that are exclusively for super_admin (enterprise-level)
    if (user?.role === "super_admin" && !selectedTenantId) {
      const onlySuper = item.roles.every((r) => r === "super_admin")
      return onlySuper
    }

    // Otherwise, show items if user's role is included
    return user && item.roles.includes(user.role)
  })

  const isImpersonating = useAuthStore((s) => s.isImpersonating)
  const stopImpersonationStore = useAuthStore((s) => s.stopImpersonation)

  return (
    <div className="flex h-screen bg-paper">
      <aside className="w-64 shrink-0 border-r border-cocoa-100 bg-white flex flex-col">
        <div
          className="flex items-center gap-2 px-5 py-5 border-b border-cocoa-100 cursor-pointer"
          onClick={() => navigate("/dashboard")}
        >
          <GraduationCap className="h-6 w-6 text-cocoa-600" />
          <span className="font-display font-semibold text-lg">EUMP</span>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto scrollbar-thin">
          {visibleItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-cocoa-100 text-cocoa-800"
                    : "text-cocoa-500 hover:bg-cocoa-50 hover:text-cocoa-700"
                )
              }
            >
              {item.icon}
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-cocoa-100 px-4 py-4 space-y-4">
          {user?.role === "super_admin" && tenantQuery.data && (
            <TenantSwitcher tenants={tenantQuery.data} />
          )}

          <div>
            <p className="text-sm font-medium text-ink truncate">
              {user?.first_name} {user?.last_name}
            </p>
            <p className="text-xs text-cocoa-400 font-mono uppercase truncate">
              {user?.role.replace(/_/g, " ")}
            </p>
          </div>

          <button
            onClick={() => {
              setSelectedTenantId(null)
              logout()
            }}
            className="flex items-center gap-2 text-sm text-cocoa-500 hover:text-red-600 transition-colors"
          >
            <LogOut className="h-4 w-4" />
            Sign out
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto scrollbar-thin">
        <div className="max-w-6xl mx-auto px-8 py-8">
          {isImpersonating && (
            <div className="mb-4 rounded border-l-4 border-yellow-400 bg-yellow-50 px-4 py-3 flex items-center justify-between">
              <div className="text-sm text-yellow-800">Impersonation active: acting as tenant <span className="font-mono">{selectedTenantId}</span></div>
              <div>
                <button
                  onClick={async () => {
                    try {
                      await adminApi.stopImpersonation(selectedTenantId ?? undefined)
                    } catch (e) {
                      // ignore
                    }
                    stopImpersonationStore()
                    setSelectedTenantId(null)
                    navigate("/dashboard")
                  }}
                  className="btn btn-sm"
                >
                  Stop impersonation
                </button>
              </div>
            </div>
          )}
          {children}
        </div>
      </main>
    </div>
  )
}
