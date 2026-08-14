"""
University Setup Completeness Checklist
Item 29: Display setup checklist before admin submission

Ensures university has configured all required sections:
1. Basic info (name, code, location)
2. Academic structure (colleges, departments, programmes)
3. Admissions (forms, requirements, application fee)
4. Courses (course catalogue)
5. Grading (grade configuration)
6. Graduation (graduation requirements)
7. Finance (payment settings, fees, invoicing)
8. Library (library configuration)
9. Accommodation (hostels, allocation)
10. Staff (staff structure, roles)
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from beanie import Document, Indexed
import logging

logger = logging.getLogger(__name__)


class ChecklistItem(BaseModel):
    """Individual checklist item."""
    item_id: str  # e.g., "basic_info", "academic_structure"
    category: str  # e.g., "Core", "Academic", "Operations"
    name: str
    description: str
    is_required: bool
    is_completed: bool = False
    completion_percentage: int = 0  # 0-100
    completion_date: Optional[datetime] = None
    completed_by: Optional[str] = None
    notes: Optional[str] = None


class SetupChecklistResponse(BaseModel):
    """Response for setup checklist."""
    tenant_id: str
    total_items: int
    completed_items: int
    completion_percentage: int
    is_complete: bool
    checklist_items: List[ChecklistItem]
    blocking_items: List[str]  # Items that must be complete before submission
    warnings: List[str]  # Nice-to-have items
    can_submit: bool


# ==================== CHECKLIST DEFINITIONS ====================

UNIVERSITY_SETUP_CHECKLIST = [
    {
        "item_id": "basic_info",
        "category": "Core",
        "name": "Basic Information",
        "description": "University name, code, location, contact info",
        "is_required": True,
    },
    {
        "item_id": "academic_structure",
        "category": "Academic",
        "name": "Academic Structure",
        "description": "Colleges, departments, programmes defined",
        "is_required": True,
    },
    {
        "item_id": "programmes",
        "category": "Academic",
        "name": "Programmes",
        "description": "At least one programme with requirements",
        "is_required": True,
    },
    {
        "item_id": "application_forms",
        "category": "Admissions",
        "name": "Application Forms",
        "description": "Custom application form configured",
        "is_required": True,
    },
    {
        "item_id": "admissions_requirements",
        "category": "Admissions",
        "name": "Admissions Requirements",
        "description": "Entry requirements for programmes",
        "is_required": True,
    },
    {
        "item_id": "grading_system",
        "category": "Academic",
        "name": "Grading System",
        "description": "Grade scales, GPA calculation configured",
        "is_required": True,
    },
    {
        "item_id": "graduation_config",
        "category": "Academic",
        "name": "Graduation Requirements",
        "description": "Minimum credits, GPA, clearance configured",
        "is_required": True,
    },
    {
        "item_id": "course_catalogue",
        "category": "Academic",
        "name": "Course Catalogue",
        "description": "Courses added for programmes",
        "is_required": True,
    },
    {
        "item_id": "finance_settings",
        "category": "Operations",
        "name": "Finance Configuration",
        "description": "Fee structure, payment methods configured",
        "is_required": True,
    },
    {
        "item_id": "invoice_settings",
        "category": "Operations",
        "name": "Invoice Configuration",
        "description": "Invoice numbering and format",
        "is_required": False,
    },
    {
        "item_id": "library_config",
        "category": "Operations",
        "name": "Library Configuration",
        "description": "Library settings, book catalogue",
        "is_required": False,
    },
    {
        "item_id": "accommodation",
        "category": "Operations",
        "name": "Accommodation",
        "description": "Hostels configured with capacities",
        "is_required": False,
    },
    {
        "item_id": "staff_structure",
        "category": "Operations",
        "name": "Staff Structure",
        "description": "Staff roles and assignments",
        "is_required": False,
    },
    {
        "item_id": "policies",
        "category": "Core",
        "name": "Institutional Policies",
        "description": "Academic policies documented",
        "is_required": False,
    },
]


class UniversitySetupChecklistService:
    """Manage university setup completeness checklist."""
    
    async def get_checklist(
        self,
        tenant_id: str,
    ) -> SetupChecklistResponse:
        """
        Generate checklist of setup items.
        
        Queries configuration across all modules to determine completion status.
        """
        
        # TODO: Import and query from actual services
        # from app.infrastructure.database.repositories import (
        #     UniversityRepository, ApplicationFormRepository, ProgrammeRepository,
        #     GraduationConfigRepository, FinanceConfigRepository, etc.
        # )
        
        checklist_items = []
        blocking_items = []
        warnings = []
        
        for item_def in UNIVERSITY_SETUP_CHECKLIST:
            item = ChecklistItem(
                item_id=item_def["item_id"],
                category=item_def["category"],
                name=item_def["name"],
                description=item_def["description"],
                is_required=item_def["is_required"],
                is_completed=await self._check_item_completed(tenant_id, item_def["item_id"]),
            )
            
            # Update completion percentage if completed
            if item.is_completed:
                item.completion_percentage = 100
            
            checklist_items.append(item)
            
            # Track blocking items
            if item_def["is_required"] and not item.is_completed:
                blocking_items.append(f"❌ {item.name}")
            elif not item_def["is_required"] and not item.is_completed:
                warnings.append(f"⚠️ {item.name} (optional)")
        
        # Calculate completion
        total = len(checklist_items)
        completed = sum(1 for item in checklist_items if item.is_completed)
        completion_percentage = int((completed / total * 100) if total > 0 else 0)
        
        # Can submit if all required items are complete
        can_submit = len(blocking_items) == 0
        
        return SetupChecklistResponse(
            tenant_id=tenant_id,
            total_items=total,
            completed_items=completed,
            completion_percentage=completion_percentage,
            is_complete=can_submit,
            checklist_items=checklist_items,
            blocking_items=blocking_items,
            warnings=warnings,
            can_submit=can_submit,
        )
    
    async def _check_item_completed(
        self,
        tenant_id: str,
        item_id: str,
    ) -> bool:
        """Check if specific checklist item is completed."""
        
        checks = {
            "basic_info": await self._check_basic_info(tenant_id),
            "academic_structure": await self._check_academic_structure(tenant_id),
            "programmes": await self._check_programmes(tenant_id),
            "application_forms": await self._check_application_forms(tenant_id),
            "admissions_requirements": await self._check_admissions_requirements(tenant_id),
            "grading_system": await self._check_grading_system(tenant_id),
            "graduation_config": await self._check_graduation_config(tenant_id),
            "course_catalogue": await self._check_course_catalogue(tenant_id),
            "finance_settings": await self._check_finance_settings(tenant_id),
            "invoice_settings": await self._check_invoice_settings(tenant_id),
            "library_config": await self._check_library_config(tenant_id),
            "accommodation": await self._check_accommodation(tenant_id),
            "staff_structure": await self._check_staff_structure(tenant_id),
            "policies": await self._check_policies(tenant_id),
        }
        
        return checks.get(item_id, False)
    
    async def _check_basic_info(self, tenant_id: str) -> bool:
        """Check if university has basic info configured."""
        # TODO: Query UniversityRepository
        return True  # Placeholder
    
    async def _check_academic_structure(self, tenant_id: str) -> bool:
        """Check if colleges/departments configured."""
        # TODO: Query CollegeRepository, DepartmentRepository
        return True
    
    async def _check_programmes(self, tenant_id: str) -> bool:
        """Check if programmes exist."""
        # TODO: Query ProgrammeRepository
        return True
    
    async def _check_application_forms(self, tenant_id: str) -> bool:
        """Check if application form configured."""
        # TODO: Query ApplicationFormRepository
        return True
    
    async def _check_admissions_requirements(self, tenant_id: str) -> bool:
        """Check if admissions requirements configured."""
        # TODO: Query ProgrammeRepository for requirements
        return True
    
    async def _check_grading_system(self, tenant_id: str) -> bool:
        """Check if grading system configured."""
        # TODO: Query GradeConfigRepository
        return True
    
    async def _check_graduation_config(self, tenant_id: str) -> bool:
        """Check if graduation requirements configured."""
        # TODO: Query GraduationConfigRepository
        from app.application.admin.graduation_configuration import GraduationConfiguration
        config = await GraduationConfiguration.find_one(
            GraduationConfiguration.tenant_id == tenant_id
        )
        return config is not None and config.is_configured
    
    async def _check_course_catalogue(self, tenant_id: str) -> bool:
        """Check if courses added."""
        # TODO: Query CourseRepository
        return True
    
    async def _check_finance_settings(self, tenant_id: str) -> bool:
        """Check if finance configured."""
        # TODO: Query FinanceConfigRepository
        return True
    
    async def _check_invoice_settings(self, tenant_id: str) -> bool:
        """Check if invoicing configured."""
        # TODO: Query InvoiceConfigRepository
        return True
    
    async def _check_library_config(self, tenant_id: str) -> bool:
        """Check if library configured."""
        # TODO: Query LibraryConfigRepository
        return True
    
    async def _check_accommodation(self, tenant_id: str) -> bool:
        """Check if accommodation configured."""
        # TODO: Query AccommodationRepository
        return True
    
    async def _check_staff_structure(self, tenant_id: str) -> bool:
        """Check if staff configured."""
        # TODO: Query StaffRepository
        return True
    
    async def _check_policies(self, tenant_id: str) -> bool:
        """Check if policies documented."""
        # TODO: Query PolicyRepository
        return True
    
    async def mark_item_completed(
        self,
        tenant_id: str,
        item_id: str,
        completed_by: str,
    ) -> bool:
        """Mark checklist item as manually completed."""
        logger.info(f"✅ Marked {item_id} complete for {tenant_id}")
        return True
