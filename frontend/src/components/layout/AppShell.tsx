import { type ReactNode } from "react"
import { NavLink, useNavigate } from "react-router-dom"
import { useAuthStore } from "@/store/authStore"
import { useLogout } from "@/hooks/useAuth"
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

  // APPLICANT ONLY
  { label: "My Application", path: "/apply/status", icon: <FileCheck className="h-4 w-4" />, roles: ["applicant"] },

  // STUDENT ONLY
  { label: "Course Registration", path: "/academic/registration", icon: <BookOpen className="h-4 w-4" />, roles: ["student"] },
  { label: "My Timetable", path: "/student/timetable", icon: <CalendarCheck className="h-4 w-4" />, roles: ["student"] },
  { label: "Exam Results", path: "/student/results", icon: <ClipboardList className="h-4 w-4" />, roles: ["student"] },
  { label: "My Payments", path: "/finance/payments", icon: <Wallet className="h-4 w-4" />, roles: ["student"] },
  { label: "Accommodation", path: "/accommodation", icon: <Building2 className="h-4 w-4" />, roles: ["student"] },
  { label: "Library", path: "/library", icon: <LibraryIcon className="h-4 w-4" />, roles: ["student"] },
  { label: "Health Services", path: "/health", icon: <HeartPulse className="h-4 w-4" />, roles: ["student"] },
  { label: "My Documents", path: "/documents", icon: <FileText className="h-4 w-4" />, roles: ["student"] },
  { label: "Alumni Network", path: "/alumni", icon: <AlumniIcon className="h-4 w-4" />, roles: ["student"] },

  // LECTURER ONLY
  { label: "My Workspace", path: "/officer/dashboard/lecturer", icon: <BookOpen className="h-4 w-4" />, roles: ["lecturer"] },
  { label: "My Courses", path: "/lecturer", icon: <BookOpen className="h-4 w-4" />, roles: ["lecturer"] },
  { label: "My Grades", path: "/exam/my-grades", icon: <ClipboardList className="h-4 w-4" />, roles: ["lecturer"] },
  { label: "Submit Grades", path: "/exam/submit-grades", icon: <ClipboardList className="h-4 w-4" />, roles: ["lecturer"] },
  { label: "Research", path: "/research", icon: <FlaskConical className="h-4 w-4" />, roles: ["lecturer"] },
  { label: "Courses & Materials", path: "/lecturer/courses", icon: <BookOpen className="h-4 w-4" />, roles: ["lecturer"] },

  // HEAD OF DEPARTMENT
  { label: "Department Workspace", path: "/officer/dashboard/hod", icon: <Settings className="h-4 w-4" />, roles: ["head_of_department"] },
  { label: "Department", path: "/head-of-department", icon: <Settings className="h-4 w-4" />, roles: ["head_of_department"] },
  { label: "Approve Grades (HOD)", path: "/exam/approve-grades", icon: <ClipboardCheck className="h-4 w-4" />, roles: ["head_of_department"] },
  { label: "Approve Leaves", path: "/hr/approve-leaves", icon: <Briefcase className="h-4 w-4" />, roles: ["head_of_department"] },

  // DEAN
  { label: "Faculty Workspace", path: "/officer/dashboard/dean", icon: <ShieldCheck className="h-4 w-4" />, roles: ["dean"] },
  { label: "Faculty", path: "/dean", icon: <ShieldCheck className="h-4 w-4" />, roles: ["dean"] },
  { label: "Approve Grades (Dean)", path: "/exam/approve-grades", icon: <ClipboardCheck className="h-4 w-4" />, roles: ["dean"] },

  // REGISTRAR
  { label: "Registrar Workspace", path: "/officer/dashboard/registrar", icon: <Users className="h-4 w-4" />, roles: ["registrar"] },
  { label: "Registrar Dashboard", path: "/registrar", icon: <Users className="h-4 w-4" />, roles: ["registrar"] },
  { label: "All Applicants", path: "/officer/applicants", icon: <Users className="h-4 w-4" />, roles: ["registrar"] },
  { label: "Approve Grades (Registrar)", path: "/exam/approve-grades", icon: <ClipboardCheck className="h-4 w-4" />, roles: ["registrar"] },

  // ADMISSIONS OFFICER
  { label: "Admissions Workspace", path: "/officer/dashboard/admissions", icon: <FileCheck className="h-4 w-4" />, roles: ["admissions_officer"] },
  { label: "Pending Results", path: "/officer/pending-results", icon: <FileCheck className="h-4 w-4" />, roles: ["admissions_officer"] },
  { label: "Applicants", path: "/officer/applicants", icon: <Users className="h-4 w-4" />, roles: ["admissions_officer"] },
  { label: "Process Admissions", path: "/officer/processing", icon: <Settings className="h-4 w-4" />, roles: ["admissions_officer"] },

  // FINANCE OFFICER
  { label: "Finance Workspace", path: "/officer/dashboard/finance", icon: <Wallet className="h-4 w-4" />, roles: ["finance_officer"] },
  { label: "Finance Dashboard", path: "/finance/officer", icon: <Wallet className="h-4 w-4" />, roles: ["finance_officer"] },
  { label: "Payments", path: "/finance/payments", icon: <Wallet className="h-4 w-4" />, roles: ["finance_officer"] },

  // HOSTEL ADMINISTRATOR
  { label: "Hostel Workspace", path: "/officer/dashboard/hostel", icon: <Building2 className="h-4 w-4" />, roles: ["hostel_administrator", "hostel_admin", "hostel_manager", "hostel_officer", "accommodation_officer", "housing_officer"] },
  { label: "Hostel Management", path: "/hostel", icon: <Building2 className="h-4 w-4" />, roles: ["hostel_administrator", "hostel_admin", "hostel_manager", "hostel_officer", "accommodation_officer", "housing_officer"] },

  // LIBRARIAN
  { label: "Library Workspace", path: "/officer/dashboard/librarian", icon: <LibraryIcon className="h-4 w-4" />, roles: ["librarian"] },
  { label: "Library Management", path: "/librarian", icon: <LibraryIcon className="h-4 w-4" />, roles: ["librarian"] },

  // EXAMINATION OFFICER
  { label: "Exam Workspace", path: "/officer/dashboard/exam", icon: <ClipboardCheck className="h-4 w-4" />, roles: ["examination_officer"] },

  // COUNSELOR
  { label: "Counselor Inbox", path: "/counselor", icon: <HeartPulse className="h-4 w-4" />, roles: ["counselor"] },

  // AUDITOR
  { label: "Audit Reports", path: "/auditor", icon: <FileText className="h-4 w-4" />, roles: ["auditor"] },

  // UNIVERSITY ADMIN / SINGLE-UNIVERSITY MODE
  { label: "Admin Dashboard", path: "/admin", icon: <ShieldCheck className="h-4 w-4" />, roles: ["university_admin"] },
  { label: "Manage Users", path: "/admin/users", icon: <Users className="h-4 w-4" />, roles: ["university_admin"] },
  { label: "Role Setup", path: "/admin/role-setup", icon: <Users className="h-4 w-4" />, roles: ["university_admin"] },
  { label: "Academic Setup", path: "/admin/academic-setup", icon: <BookOpen className="h-4 w-4" />, roles: ["university_admin"] },
  { label: "University Setup Wizard", path: "/admin/university-setup", icon: <FileCheck className="h-4 w-4" />, roles: ["university_admin"] },
  { label: "University Settings", path: "/admin/university-settings", icon: <Settings className="h-4 w-4" />, roles: ["university_admin"] },

  // SYSTEM ADMIN (single-university deployment)
  { label: "University Administration", path: "/admin", icon: <ShieldCheck className="h-4 w-4" />, roles: ["super_admin"] },
  { label: "University Applications", path: "/admin/university-applications", icon: <FileCheck className="h-4 w-4" />, roles: ["super_admin"] },
  { label: "Application Review", path: "/admin/super-admin-review", icon: <FileCheck className="h-4 w-4" />, roles: ["super_admin"] },

  // SHARED/COMMON - visible to most roles but filtered
  { label: "Notifications", path: "/communication/notifications", icon: <Bell className="h-4 w-4" />, roles: ["student", "lecturer", "head_of_department", "dean", "registrar", "admissions_officer", "finance_officer", "university_admin", "super_admin"] },
  { label: "My Tasks", path: "/workflow/tasks", icon: <GitBranch className="h-4 w-4" />, roles: ["registrar", "admissions_officer", "head_of_department", "dean", "university_admin", "super_admin"] },
]

export function AppShell({ children }: { children: ReactNode }) {
  const user = useAuthStore((s) => s.user)
  const logout = useLogout()
  const navigate = useNavigate()

  const visibleItems = NAV_ITEMS.filter((item) => {
    if (!item.roles) return true
    return user && item.roles.includes(user.role)
  })

  return (
    <div className="flex h-screen bg-paper">
      <aside className="w-64 shrink-0 border-r border-cocoa-100 bg-white flex flex-col">
        <div
          className="flex items-center gap-2 px-5 py-5 border-b border-cocoa-100 cursor-pointer"
          onClick={() => navigate("/dashboard")}
        >
          <GraduationCap className="h-6 w-6 text-cocoa-600" />
          <span className="font-display font-semibold text-lg">University of Machelli</span>
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
          {children}
        </div>
      </main>
    </div>
  )
}
