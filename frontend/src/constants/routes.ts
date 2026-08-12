export const ROUTES = {
  LOGIN: "/login",
  REGISTER: "/register",
  DASHBOARD: "/dashboard",

  APPLY: "/apply",
  APPLICATION_STATUS: "/apply/status",
  SUBMIT_RESULTS: "/apply/results",

  OFFICER_PENDING_RESULTS: "/officer/pending-results",
  OFFICER_APPLICANTS: "/officer/applicants",
  OFFICER_APPLICANT_DETAIL: "/officer/applicants/:id",
  OFFICER_WAITLIST: "/officer/waitlist",
  OFFICER_PROCESSING: "/officer/processing",

  ACADEMIC_REGISTRATION: "/academic/registration",

  FINANCE_PAYMENTS: "/finance/payments",

  EXAM_SUBMIT_GRADES: "/exam/submit-grades",
  EXAM_MY_GRADES: "/exam/my-grades",
  EXAM_APPROVE_GRADES: "/exam/approve-grades",
  LECTURER_COURSE_MATERIALS: "/lecturer/courses/:courseId/materials",

  ACCOMMODATION: "/accommodation",

  REGISTRAR: "/registrar",
  HOD: "/head-of-department",
  DEAN: "/dean",
  FINANCE_OFFICER: "/finance/officer",
  SUPER_ADMIN: "/super-admin",
  AUDITOR: "/auditor",

  LIBRARY: "/library",
  LIBRARIAN: "/librarian",
  COUNSELOR: "/counselor",
  PARENT: "/parent",

  HR_REQUEST_LEAVE: "/hr/request-leave",
  HR_APPROVE_LEAVES: "/hr/approve-leaves",

  HEALTH: "/health",

  RESEARCH: "/research",

  ALUMNI: "/alumni",

  COMMUNICATION_NOTIFICATIONS: "/communication/notifications",
  COMMUNICATION_CAMPAIGNS: "/communication/campaigns",

  DOCUMENTS: "/documents",

  WORKFLOW_TASKS: "/workflow/tasks",

  INVENTORY: "/inventory",

  ANALYTICS: "/analytics",

  ADMIN_DASHBOARD: "/admin",
  ADMIN_USERS: "/admin/users",
  ADMIN_TENANT_SETTINGS: "/admin/tenant-settings",
  STUDENT_DASHBOARD: "/student",
  LECTURER_DASHBOARD: "/lecturer",
  HOSTEL_ADMIN: "/hostel",

  UNAUTHORIZED: "/unauthorized",
} as const
