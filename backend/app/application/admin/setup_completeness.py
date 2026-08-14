"""
Setup Completeness Engine
Item 64: University Setup Validation - Ensures mandatory configs are complete

Prevents university activation until all required setup is done:
1. University info (name, location, contact)
2. Programmes configured
3. Faculties/Departments configured
4. Courses configured
5. Academic calendar configured
6. Staff assigned (at least registrar, dean, hod)
7. Student ID generation configured
8. Admission cycles configured
9. Application fees configured
10. Hall of residence configured
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from app.infrastructure.models.tenant import Tenant
from app.infrastructure.database.repositories.tenant_repository import TenantRepository
from app.infrastructure.database.repositories.programme_repository import ProgrammeRepository
from app.infrastructure.database.repositories.faculty_repository import FacultyRepository
from app.infrastructure.database.repositories.course_repository import CourseRepository
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.infrastructure.database.repositories.admission_cycle_repository import AdmissionCycleRepository
from app.infrastructure.database.repositories.accommodation_repository import AccommodationRepository
import logging

logger = logging.getLogger(__name__)


class SetupCompletenessEngine:
    """Check if university setup is complete."""
    
    def __init__(
        self,
        tenant_repo: TenantRepository,
        programme_repo: ProgrammeRepository,
        faculty_repo: FacultyRepository,
        course_repo: CourseRepository,
        user_repo: UserRepository,
        admission_repo: AdmissionCycleRepository,
        accommodation_repo: AccommodationRepository,
    ):
        self.tenant_repo = tenant_repo
        self.programme_repo = programme_repo
        self.faculty_repo = faculty_repo
        self.course_repo = course_repo
        self.user_repo = user_repo
        self.admission_repo = admission_repo
        self.accommodation_repo = accommodation_repo
    
    async def check_setup_completeness(
        self,
        tenant_id: str,
    ) -> Dict[str, Any]:
        """
        Check if university setup is complete.
        
        Returns:
            {
                "is_complete": true/false,
                "completion_percentage": 85,
                "checks": {
                    "university_info": {"complete": true, "message": "..."},
                    "programmes": {"complete": true, "message": "..."},
                    ...
                },
                "missing_items": ["...", "..."],
                "blocking_issues": ["University name not set", "No programmes configured"],
            }
        """
        tenant = await self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} not found")
        
        checks = {}
        missing = []
        blocking = []
        
        # 1. University Information
        check = await self._check_university_info(tenant)
        checks["university_info"] = check
        if not check["complete"]:
            missing.append("university_info")
            if check.get("blocking"):
                blocking.append(check["message"])
        
        # 2. Programmes
        check = await self._check_programmes(tenant_id)
        checks["programmes"] = check
        if not check["complete"]:
            missing.append("programmes")
            if check.get("blocking"):
                blocking.append(check["message"])
        
        # 3. Faculties/Departments
        check = await self._check_faculties(tenant_id)
        checks["faculties_departments"] = check
        if not check["complete"]:
            missing.append("faculties_departments")
            if check.get("blocking"):
                blocking.append(check["message"])
        
        # 4. Courses
        check = await self._check_courses(tenant_id)
        checks["courses"] = check
        if not check["complete"]:
            missing.append("courses")
            if check.get("blocking"):
                blocking.append(check["message"])
        
        # 5. Staff Configuration
        check = await self._check_staff(tenant_id)
        checks["staff"] = check
        if not check["complete"]:
            missing.append("staff")
            if check.get("blocking"):
                blocking.append(check["message"])
        
        # 6. Student ID Generation
        check = await self._check_student_id_config(tenant)
        checks["student_id_generation"] = check
        if not check["complete"]:
            missing.append("student_id_generation")
            if check.get("blocking"):
                blocking.append(check["message"])
        
        # 7. Admission Cycles
        check = await self._check_admission_cycles(tenant_id)
        checks["admission_cycles"] = check
        if not check["complete"]:
            missing.append("admission_cycles")
            if check.get("blocking"):
                blocking.append(check["message"])
        
        # 8. Application Fees
        check = await self._check_application_fees(tenant)
        checks["application_fees"] = check
        if not check["complete"]:
            missing.append("application_fees")
            if check.get("blocking"):
                blocking.append(check["message"])
        
        # 9. Accommodation
        check = await self._check_accommodation(tenant_id)
        checks["accommodation"] = check
        if not check["complete"]:
            missing.append("accommodation")
        
        # 10. Academic Calendar
        check = await self._check_academic_calendar(tenant)
        checks["academic_calendar"] = check
        if not check["complete"]:
            missing.append("academic_calendar")
            if check.get("blocking"):
                blocking.append(check["message"])
        
        # Calculate completion percentage
        total_checks = len(checks)
        complete_checks = sum(1 for c in checks.values() if c.get("complete"))
        completion_percentage = int((complete_checks / total_checks) * 100) if total_checks > 0 else 0
        
        # University can only be activated if no blocking issues
        is_complete = len(blocking) == 0
        
        return {
            "is_complete": is_complete,
            "completion_percentage": completion_percentage,
            "checks": checks,
            "missing_items": missing,
            "blocking_issues": blocking,
            "summary": (
                f"Setup {completion_percentage}% complete. "
                f"{len(blocking)} blocking issues must be resolved before activation."
            ),
        }
    
    async def _check_university_info(self, tenant: Tenant) -> Dict[str, Any]:
        """Check if university info is configured."""
        issues = []
        
        if not tenant.name:
            issues.append("University name not set")
        if not tenant.code:
            issues.append("University code not set")
        if not tenant.location:
            issues.append("University location not set")
        if not tenant.contact_email:
            issues.append("University contact email not set")
        if not tenant.contact_phone:
            issues.append("University contact phone not set")
        
        return {
            "complete": len(issues) == 0,
            "blocking": len(issues) > 0,
            "message": ", ".join(issues) if issues else "University info complete",
        }
    
    async def _check_programmes(self, tenant_id: str) -> Dict[str, Any]:
        """Check if programmes are configured."""
        programmes = await self.programme_repo.find({"tenant_id": tenant_id})
        
        if not programmes:
            return {
                "complete": False,
                "blocking": True,
                "message": "No programmes configured",
            }
        
        # Check that programmes have courses
        total_programmes = len(programmes)
        programmes_with_courses = 0
        
        for prog in programmes:
            courses = await self.course_repo.find({
                "tenant_id": tenant_id,
                "programme_id": str(prog.id),
            })
            if courses:
                programmes_with_courses += 1
        
        return {
            "complete": programmes_with_courses == total_programmes,
            "blocking": programmes_with_courses < total_programmes,
            "message": f"{programmes_with_courses}/{total_programmes} programmes have courses",
        }
    
    async def _check_faculties(self, tenant_id: str) -> Dict[str, Any]:
        """Check if faculties/departments are configured."""
        faculties = await self.faculty_repo.find({"tenant_id": tenant_id})
        
        return {
            "complete": len(faculties) > 0,
            "blocking": len(faculties) == 0,
            "message": f"{len(faculties)} faculties configured",
        }
    
    async def _check_courses(self, tenant_id: str) -> Dict[str, Any]:
        """Check if courses are configured."""
        courses = await self.course_repo.find({"tenant_id": tenant_id})
        
        return {
            "complete": len(courses) > 0,
            "blocking": len(courses) == 0,
            "message": f"{len(courses)} courses configured",
        }
    
    async def _check_staff(self, tenant_id: str) -> Dict[str, Any]:
        """Check if required staff are assigned."""
        required_roles = ["registrar", "dean", "hod"]
        
        staff_by_role = {}
        for role in required_roles:
            users = await self.user_repo.find({
                "tenant_id": tenant_id,
                "role": role,
            })
            staff_by_role[role] = len(users) > 0
        
        missing_roles = [r for r in required_roles if not staff_by_role[r]]
        
        return {
            "complete": len(missing_roles) == 0,
            "blocking": len(missing_roles) > 0,
            "message": f"Missing staff: {', '.join(missing_roles)}" if missing_roles else "All required staff assigned",
        }
    
    async def _check_student_id_config(self, tenant: Tenant) -> Dict[str, Any]:
        """Check if student ID generation is configured."""
        if not hasattr(tenant, 'student_id_template') or not tenant.student_id_template:
            return {
                "complete": False,
                "blocking": True,
                "message": "Student ID template not configured",
            }
        
        return {
            "complete": True,
            "blocking": False,
            "message": f"Student ID template: {tenant.student_id_template}",
        }
    
    async def _check_admission_cycles(self, tenant_id: str) -> Dict[str, Any]:
        """Check if admission cycles are configured."""
        cycles = await self.admission_repo.find({
            "tenant_id": tenant_id,
        })
        
        if not cycles:
            return {
                "complete": False,
                "blocking": True,
                "message": "No admission cycles configured",
            }
        
        # Check that at least one cycle has dates configured
        configured = sum(
            1 for c in cycles
            if hasattr(c, 'opening_date') and hasattr(c, 'closing_date')
        )
        
        return {
            "complete": configured > 0,
            "blocking": configured == 0,
            "message": f"{configured}/{len(cycles)} cycles have dates configured",
        }
    
    async def _check_application_fees(self, tenant: Tenant) -> Dict[str, Any]:
        """Check if application fees are configured."""
        if not hasattr(tenant, 'application_fee') or tenant.application_fee is None:
            return {
                "complete": False,
                "blocking": True,
                "message": "Application fee not configured",
            }
        
        if tenant.application_fee <= 0:
            return {
                "complete": False,
                "blocking": True,
                "message": f"Invalid application fee: {tenant.application_fee}",
            }
        
        return {
            "complete": True,
            "blocking": False,
            "message": f"Application fee: {tenant.application_fee}",
        }
    
    async def _check_accommodation(self, tenant_id: str) -> Dict[str, Any]:
        """Check if accommodation/halls are configured."""
        halls = await self.accommodation_repo.find({
            "tenant_id": tenant_id,
        })
        
        return {
            "complete": len(halls) > 0,
            "blocking": False,  # Not blocking, nice-to-have
            "message": f"{len(halls)} halls of residence configured",
        }
    
    async def _check_academic_calendar(self, tenant: Tenant) -> Dict[str, Any]:
        """Check if academic calendar is configured."""
        if not hasattr(tenant, 'academic_start_date') or not tenant.academic_start_date:
            return {
                "complete": False,
                "blocking": True,
                "message": "Academic calendar not configured",
            }
        
        return {
            "complete": True,
            "blocking": False,
            "message": f"Academic year starts: {tenant.academic_start_date}",
        }
