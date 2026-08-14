import { Routes, Route, Navigate } from "react-router-dom"
import { PrivateRoute } from "./PrivateRoute"
import { ROUTES } from "@/constants/routes"

import LoginPage from "@/pages/auth/LoginPage"
import RegisterPage from "@/pages/auth/RegisterPage"
import DashboardPage from "@/pages/DashboardPage"

// Applicant Portal Pages (Section 33-34)
import ApplicantPortalLandingPage from "@/pages/applicant/ApplicantPortalLandingPage"
import ApplicantPortalLoginPage from "@/pages/applicant/ApplicantPortalLoginPage"
import ApplicantPortalRegistrationPage from "@/pages/applicant/ApplicantPortalRegistrationPage"
import ApplicantPortalDashboardPage from "@/pages/applicant/ApplicantPortalDashboardPage"
import ApplicantPortalPaymentPage from "@/pages/applicant/ApplicantPortalPaymentPage"
import ApplicantWASSCEEntryPage from "@/pages/applicant/ApplicantWASSCEEntryPage"

import ApplicationStatusPage from "@/pages/applicant/ApplicationStatusPage"
import PendingResultsPage from "@/pages/officer/PendingResultsPage"
import ApplicantsListPage from "@/pages/officer/ApplicantsListPage"
import ProcessingPage from "@/pages/officer/ProcessingPage"
import ApplicantDetailPage from "@/pages/officer/ApplicantDetailPage"
import WaitlistPage from "@/pages/officer/WaitlistPage"
import OfficerWASSCEVerificationPage from "@/pages/officer/OfficerWASSCEVerificationPage"
import AdmissionsOfficerDashboardPage from "@/pages/officer/AdmissionsOfficerDashboardPage"
import RegistrarDashboardPage from "@/pages/officer/RegistrarDashboardPage"
import HODDashboardPage from "@/pages/officer/HODDashboardPage"
import DeanDashboardPage from "@/pages/officer/DeanDashboardPage"
import FinanceOfficerDashboardPage from "@/pages/officer/FinanceOfficerDashboardPage"
import HostelAdminDashboardPage from "@/pages/officer/HostelAdminDashboardPage"
import LibrarianDashboardPage from "@/pages/officer/LibrarianDashboardPage"
import ExamOfficerDashboardPage from "@/pages/officer/ExamOfficerDashboardPage"
import StudentDashboardPageOfficer from "@/pages/officer/StudentDashboardPage"
import AlumniDashboardPage from "@/pages/officer/AlumniDashboardPage"
import TenantAdminDashboardPage from "@/pages/officer/TenantAdminDashboardPage"
import SuperAdminDashboardPage from "@/pages/officer/SuperAdminDashboardPage"
import LecturerDashboardPageV2 from "@/pages/lecturer/LecturerDashboardPageV2"

import CourseRegistrationPage from "@/pages/academic/CourseRegistrationPage"
import PaymentsPage from "@/pages/finance/PaymentsPage"
import SubmitGradesPage from "@/pages/exam/SubmitGradesPage"
import MyGradesPage from "@/pages/exam/MyGradesPage"
import ApproveGradesPage from "@/pages/exam/ApproveGradesPage"
import AccommodationPage from "@/pages/accommodation/AccommodationPage"
import LibraryPage from "@/pages/library/LibraryPage"
import LibrarianPage from "@/pages/library/LibrarianPage"
import CounselorPage from "@/pages/counseling/CounselorPage"
import ParentPortal from "@/pages/parent/ParentPortal"
import RequestLeavePage from "@/pages/hr/RequestLeavePage"
import ApproveLeavesPage from "@/pages/hr/ApproveLeavesPage"
import HealthServicesPage from "@/pages/health/HealthServicesPage"
import ResearchPage from "@/pages/research/ResearchPage"
import AlumniPage from "@/pages/alumni/AlumniPage"
import NotificationsPage from "@/pages/communication/NotificationsPage"
import CampaignsPage from "@/pages/communication/CampaignsPage"
import DocumentsPage from "@/pages/document/DocumentsPage"
import ApprovalTasksPage from "@/pages/workflow/ApprovalTasksPage"
import InventoryPage from "@/pages/inventory/InventoryPage"
import AnalyticsDashboardPage from "@/pages/analytics/AnalyticsDashboardPage"
import AdminDashboardPage from "@/pages/admin/AdminDashboardPage"
import AdminUsersPage from "@/pages/admin/AdminUsersPage"
import TenantSettingsPage from "@/pages/admin/TenantSettingsPage"
import RegistrarPage from "@/pages/admin/RegistrarPage"
import HeadOfDepartmentPage from "@/pages/admin/HeadOfDepartmentPage"
import DeanPage from "@/pages/admin/DeanPage"
import FinanceOfficerPage from "@/pages/admin/FinanceOfficerPage"
import SuperAdminPage from "@/pages/admin/SuperAdminPage"
import AuditorPage from "@/pages/admin/AuditorPage"
import UniversityApplicationsPage from "@/pages/admin/UniversityApplicationsPage"
import StudentDashboardPage from "@/pages/student/StudentDashboardPage"
import LecturerDashboardPage from "@/pages/lecturer/LecturerDashboardPage"
import AttendancePage from "@/pages/lecturer/AttendancePage"
import LecturerRosterPage from "@/pages/lecturer/LecturerRosterPage"
import AttendanceReportPage from "@/pages/lecturer/AttendanceReportPage"
import CourseMaterialsPage from "@/pages/lecturer/CourseMaterialsPage"
import GradeSubmissionPage from "@/pages/lecturer/GradeSubmissionPage"
import GradeStatisticsPage from "@/pages/lecturer/GradeStatisticsPage"
import QRCodeAttendancePage from "@/pages/attendance/QRCodeAttendancePage"
import PublicAttendanceForm from "@/pages/attendance/PublicAttendanceForm"
import HostelAdminPage from "@/pages/accommodation/HostelAdminPage"

import UnauthorizedPage from "@/pages/UnauthorizedPage"
import NotFoundPage from "@/pages/NotFoundPage"

const OFFICER_ROLES = ["admissions_officer", "registrar", "university_admin", "super_admin"]
const ADMIN_ROLES = ["university_admin", "super_admin"]
const LECTURER_ROLES = ["lecturer", "head_of_department", "dean"]
const GRADE_APPROVER_ROLES = ["head_of_department", "dean", "registrar"]
const STAFF_MGMT_ROLES = ["hostel_administrator", "librarian", "university_admin", "super_admin"]
const COUNSELOR_ROLES = ["counselor", "university_admin", "super_admin"]
const PARENT_ROLES = ["parent_guardian", "university_admin", "super_admin"]
const LEAVE_APPROVER_ROLES = ["head_of_department", "university_admin", "super_admin"]
const RESEARCH_ROLES = ["lecturer", "dean", "head_of_department"]
const ANALYTICS_ROLES = ["admissions_officer", "registrar", "finance_officer", "university_admin", "super_admin"]
const COMMS_ADMIN_ROLES = ["university_admin", "super_admin", "registrar"]

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to={ROUTES.DASHBOARD} replace />} />
      <Route path={ROUTES.LOGIN} element={<LoginPage />} />
      <Route path={ROUTES.REGISTER} element={<RegisterPage />} />
      <Route path={ROUTES.UNAUTHORIZED} element={<UnauthorizedPage />} />

      {/* Applicant Portal Routes (Section 33-34) */}
      <Route path="/apply/:schoolCode" element={<ApplicantPortalLandingPage />} />
      <Route path="/apply/:schoolCode/login" element={<ApplicantPortalLoginPage />} />
      <Route path="/apply/:schoolCode/register" element={<ApplicantPortalRegistrationPage />} />
      <Route path="/apply/:schoolCode/dashboard" element={<ApplicantPortalDashboardPage />} />
      <Route path="/apply/:schoolCode/payment" element={<ApplicantPortalPaymentPage />} />
      <Route path="/apply/:schoolCode/wassce" element={<ApplicantWASSCEEntryPage />} />
      {/* Additional applicant portal pages will be added in next sections */}

      <Route path={ROUTES.DASHBOARD} element={<PrivateRoute><DashboardPage /></PrivateRoute>} />

      {/* Admissions */}
      <Route path={ROUTES.APPLICATION_STATUS} element={<PrivateRoute><ApplicationStatusPage /></PrivateRoute>} />
      {/* Officer Dashboards */}
      <Route
        path="/officer/dashboard/admissions"
        element={<PrivateRoute allowedRoles={OFFICER_ROLES}><AdmissionsOfficerDashboardPage /></PrivateRoute>}
      />
      <Route
        path="/officer/dashboard/registrar"
        element={<PrivateRoute allowedRoles={OFFICER_ROLES}><RegistrarDashboardPage /></PrivateRoute>}
      />
      <Route
        path="/officer/dashboard/lecturer"
        element={<PrivateRoute allowedRoles={["lecturer", "head_of_department", "dean"]}><LecturerDashboardPageV2 /></PrivateRoute>}
      />
      <Route
        path="/officer/dashboard/hod"
        element={<PrivateRoute allowedRoles={["head_of_department", "dean", "university_admin", "super_admin"]}><HODDashboardPage /></PrivateRoute>}
      />
      <Route
        path="/officer/dashboard/dean"
        element={<PrivateRoute allowedRoles={["dean", "university_admin", "super_admin"]}><DeanDashboardPage /></PrivateRoute>}
      />
      <Route
        path="/officer/dashboard/finance"
        element={<PrivateRoute allowedRoles={["finance_officer", "university_admin", "super_admin"]}><FinanceOfficerDashboardPage /></PrivateRoute>}
      />
      <Route
        path="/officer/dashboard/hostel"
        element={<PrivateRoute allowedRoles={["hostel_administrator", "university_admin", "super_admin"]}><HostelAdminDashboardPage /></PrivateRoute>}
      />
      <Route
        path="/officer/dashboard/librarian"
        element={<PrivateRoute allowedRoles={["librarian", "university_admin", "super_admin"]}><LibrarianDashboardPage /></PrivateRoute>}
      />
      <Route
        path="/officer/dashboard/exam"
        element={<PrivateRoute allowedRoles={["examination_officer", "university_admin", "super_admin"]}><ExamOfficerDashboardPage /></PrivateRoute>}
      />
      <Route
        path="/officer/dashboard/student"
        element={<PrivateRoute allowedRoles={["student"]}><StudentDashboardPageOfficer /></PrivateRoute>}
      />
      <Route
        path="/officer/dashboard/alumni"
        element={<PrivateRoute allowedRoles={["alumni_officer", "university_admin", "super_admin"]}><AlumniDashboardPage /></PrivateRoute>}
      />
      <Route
        path="/officer/dashboard/tenant_admin"
        element={<PrivateRoute allowedRoles={["university_admin"]}><TenantAdminDashboardPage /></PrivateRoute>}
      />
      <Route
        path="/officer/dashboard/super_admin"
        element={<PrivateRoute allowedRoles={["super_admin"]}><SuperAdminDashboardPage /></PrivateRoute>}
      />
      <Route
        path="/officer/wassce-verification"
        element={<PrivateRoute allowedRoles={OFFICER_ROLES}><OfficerWASSCEVerificationPage /></PrivateRoute>}
      />
      <Route
        path={ROUTES.OFFICER_PENDING_RESULTS}
        element={<PrivateRoute allowedRoles={OFFICER_ROLES}><PendingResultsPage /></PrivateRoute>}
      />
      <Route
        path={ROUTES.OFFICER_APPLICANTS}
        element={<PrivateRoute allowedRoles={OFFICER_ROLES}><ApplicantsListPage /></PrivateRoute>}
      />
      <Route
        path={ROUTES.OFFICER_PROCESSING}
        element={<PrivateRoute allowedRoles={OFFICER_ROLES}><ProcessingPage /></PrivateRoute>}
      />
      <Route
        path={ROUTES.OFFICER_WAITLIST}
        element={<PrivateRoute allowedRoles={OFFICER_ROLES}><WaitlistPage /></PrivateRoute>}
      />
      <Route
        path={ROUTES.OFFICER_APPLICANT_DETAIL}
        element={<PrivateRoute allowedRoles={OFFICER_ROLES}><ApplicantDetailPage /></PrivateRoute>}
      />

      {/* Academic */}
      <Route path={ROUTES.ACADEMIC_REGISTRATION} element={<PrivateRoute><CourseRegistrationPage /></PrivateRoute>} />

      {/* Finance */}
      <Route path={ROUTES.FINANCE_PAYMENTS} element={<PrivateRoute><PaymentsPage /></PrivateRoute>} />

      {/* Exam */}
      <Route
        path={ROUTES.EXAM_SUBMIT_GRADES}
        element={<PrivateRoute allowedRoles={LECTURER_ROLES}><SubmitGradesPage /></PrivateRoute>}
      />
      <Route
        path={ROUTES.EXAM_MY_GRADES}
        element={<PrivateRoute allowedRoles={LECTURER_ROLES}><MyGradesPage /></PrivateRoute>}
      />
      <Route
        path={ROUTES.EXAM_APPROVE_GRADES}
        element={<PrivateRoute allowedRoles={GRADE_APPROVER_ROLES}><ApproveGradesPage /></PrivateRoute>}
      />

      {/* Accommodation */}
      <Route path={ROUTES.ACCOMMODATION} element={<PrivateRoute><AccommodationPage /></PrivateRoute>} />

      {/* Library */}
      <Route path={ROUTES.LIBRARY} element={<PrivateRoute><LibraryPage /></PrivateRoute>} />
      <Route path={ROUTES.LIBRARIAN} element={<PrivateRoute allowedRoles={["librarian","university_admin","super_admin"]}><LibrarianPage /></PrivateRoute>} />
      <Route path={ROUTES.COUNSELOR} element={<PrivateRoute allowedRoles={COUNSELOR_ROLES}><CounselorPage /></PrivateRoute>} />
      <Route path={ROUTES.PARENT} element={<PrivateRoute allowedRoles={PARENT_ROLES}><ParentPortal /></PrivateRoute>} />

      {/* HR */}
      <Route path={ROUTES.HR_REQUEST_LEAVE} element={<PrivateRoute><RequestLeavePage /></PrivateRoute>} />
      <Route
        path={ROUTES.HR_APPROVE_LEAVES}
        element={<PrivateRoute allowedRoles={LEAVE_APPROVER_ROLES}><ApproveLeavesPage /></PrivateRoute>}
      />

      {/* Health */}
      <Route path={ROUTES.HEALTH} element={<PrivateRoute><HealthServicesPage /></PrivateRoute>} />

      {/* Research */}
      <Route
        path={ROUTES.RESEARCH}
        element={<PrivateRoute allowedRoles={RESEARCH_ROLES}><ResearchPage /></PrivateRoute>}
      />

      {/* Alumni */}
      <Route path={ROUTES.ALUMNI} element={<PrivateRoute><AlumniPage /></PrivateRoute>} />

      {/* Communication */}
      <Route path={ROUTES.COMMUNICATION_NOTIFICATIONS} element={<PrivateRoute><NotificationsPage /></PrivateRoute>} />
      <Route
        path={ROUTES.COMMUNICATION_CAMPAIGNS}
        element={<PrivateRoute allowedRoles={COMMS_ADMIN_ROLES}><CampaignsPage /></PrivateRoute>}
      />

      {/* Document */}
      <Route path={ROUTES.DOCUMENTS} element={<PrivateRoute><DocumentsPage /></PrivateRoute>} />

      {/* Workflow */}
      <Route path={ROUTES.WORKFLOW_TASKS} element={<PrivateRoute><ApprovalTasksPage /></PrivateRoute>} />

      {/* Inventory */}
      <Route
        path={ROUTES.INVENTORY}
        element={<PrivateRoute allowedRoles={ADMIN_ROLES}><InventoryPage /></PrivateRoute>}
      />

      {/* Analytics */}
      <Route
        path={ROUTES.ANALYTICS}
        element={<PrivateRoute allowedRoles={ANALYTICS_ROLES}><AnalyticsDashboardPage /></PrivateRoute>}
      />

      {/* Admin */}
      <Route
        path={ROUTES.ADMIN_DASHBOARD}
        element={<PrivateRoute allowedRoles={ADMIN_ROLES}><AdminDashboardPage /></PrivateRoute>}
      />
      <Route
        path={ROUTES.ADMIN_USERS}
        element={<PrivateRoute allowedRoles={ADMIN_ROLES}><AdminUsersPage /></PrivateRoute>}
      />
      <Route
        path={ROUTES.ADMIN_TENANT_SETTINGS}
        element={<PrivateRoute allowedRoles={ADMIN_ROLES}><TenantSettingsPage /></PrivateRoute>}
      />
      <Route
        path={ROUTES.REGISTRAR}
        element={<PrivateRoute allowedRoles={["registrar", "university_admin", "super_admin"]}><RegistrarPage /></PrivateRoute>}
      />
      <Route
        path={ROUTES.HOD}
        element={<PrivateRoute allowedRoles={["head_of_department", "university_admin", "super_admin"]}><HeadOfDepartmentPage /></PrivateRoute>}
      />
      <Route
        path={ROUTES.DEAN}
        element={<PrivateRoute allowedRoles={["dean", "university_admin", "super_admin"]}><DeanPage /></PrivateRoute>}
      />
      <Route
        path={ROUTES.FINANCE_OFFICER}
        element={<PrivateRoute allowedRoles={["finance_officer", "university_admin", "super_admin"]}><FinanceOfficerPage /></PrivateRoute>}
      />
      <Route
        path={ROUTES.SUPER_ADMIN}
        element={<PrivateRoute allowedRoles={["super_admin"]}><SuperAdminPage /></PrivateRoute>}
      />
      <Route
        path={ROUTES.AUDITOR}
        element={<PrivateRoute allowedRoles={["auditor", "university_admin", "super_admin"]}><AuditorPage /></PrivateRoute>}
      />
      <Route
        path={ROUTES.ADMIN_UNIVERSITY_APPLICATIONS}
        element={<PrivateRoute allowedRoles={["super_admin", "university_admin"]}><UniversityApplicationsPage /></PrivateRoute>}
      />
      <Route
        path={ROUTES.STUDENT_DASHBOARD}
        element={<PrivateRoute allowedRoles={["student"]}><StudentDashboardPage /></PrivateRoute>}
      />
      <Route
        path={ROUTES.LECTURER_DASHBOARD}
        element={<PrivateRoute allowedRoles={["lecturer"]}><LecturerDashboardPage /></PrivateRoute>}
      />
      <Route
        path={"/lecturer/courses/:courseId/materials"}
        element={<PrivateRoute allowedRoles={["lecturer"]}><CourseMaterialsPage /></PrivateRoute>}
      />
      <Route
        path={"/lecturer/courses/:courseId/attendance"}
        element={<PrivateRoute allowedRoles={["lecturer"]}><AttendancePage /></PrivateRoute>}
      />
      <Route
        path={"/lecturer/courses/:courseId/roster"}
        element={<PrivateRoute allowedRoles={["lecturer"]}><LecturerRosterPage /></PrivateRoute>}
      />
      <Route
        path={"/lecturer/courses/:courseId/attendance/report"}
        element={<PrivateRoute allowedRoles={["lecturer"]}><AttendanceReportPage /></PrivateRoute>}
      />
      <Route
        path={"/lecturer/grades/submit"}
        element={<PrivateRoute allowedRoles={["lecturer"]}><GradeSubmissionPage /></PrivateRoute>}
      />
      <Route
        path={"/lecturer/grades/statistics"}
        element={<PrivateRoute allowedRoles={["lecturer"]}><GradeStatisticsPage /></PrivateRoute>}
      />
      <Route
        path={"/attendance/mark/:courseId/:sessionId"}
        element={<PrivateRoute><QRCodeAttendancePage /></PrivateRoute>}
      />
      <Route
        path={"/attendance/public/mark/:courseId/:sessionId"}
        element={<PublicAttendanceForm />}
      />
      <Route
        path={ROUTES.HOSTEL_ADMIN}
        element={<PrivateRoute allowedRoles={["hostel_administrator","university_admin","super_admin"]}><HostelAdminPage /></PrivateRoute>}
      />

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}
