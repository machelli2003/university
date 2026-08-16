from datetime import datetime
from typing import Optional, Dict, Any
from app.infrastructure.database.repositories.university_application_repository import UniversityApplicationRepository
from app.infrastructure.database.repositories.tenant_repository import TenantRepository
from app.application.identifiers.identifier_service import IdentifierService
from app.infrastructure.models.university_application import UniversityApplicationStatusEnum
from app.infrastructure.models.tenant import SubscriptionTierEnum
from app.domain.onboarding.setup_completeness_service import SetupCompletenessService
from app.application.notifications.setup_review_notifications import (
    notify_super_admins_for_application,
    notify_application_admin,
)


class UniversityApplicationUseCase:
    def __init__(
        self,
        application_repo: UniversityApplicationRepository,
        tenant_repo: TenantRepository,
        identifier_service: IdentifierService,
    ):
        self.application_repo = application_repo
        self.tenant_repo = tenant_repo
        self.identifier_service = identifier_service

    async def create_application(
        self,
        legal_name: str,
        display_name: str,
        school_code: str,
        requested_by: str,
        admin_first_name: str,
        admin_last_name: str,
        admin_email: str,
        **metadata,
    ):
        application_id = await self.identifier_service.generate_university_application_id()
        application = await self.application_repo.create({
            "university_application_id": application_id,
            "legal_name": legal_name,
            "display_name": display_name,
            "school_code": school_code,
            "requested_by": requested_by,
            "admin_first_name": admin_first_name,
            "admin_last_name": admin_last_name,
            "admin_email": admin_email,
            "status": UniversityApplicationStatusEnum.PENDING_SETUP,
            "submitted_at": None,
            **metadata,
        })
        return application

    async def update_application(
        self,
        application_id: str,
        update_fields: Dict[str, Optional[str]],
    ):
        application = await self.application_repo.get_by_application_id(application_id)
        if not application:
            raise ValueError("University application not found")
        if application.status in [
            UniversityApplicationStatusEnum.APPROVED,
            UniversityApplicationStatusEnum.ACTIVE,
            UniversityApplicationStatusEnum.PROVISIONING,
        ]:
            raise ValueError("Cannot edit an application after approval or activation")

        update_fields["updated_at"] = datetime.utcnow()
        return await self.application_repo.update(application.id, update_fields)

    async def update_setup_section(
        self,
        application_id: str,
        section: str,
        completed: bool,
    ):
        application = await self.application_repo.get_by_application_id(application_id)
        if not application:
            raise ValueError("University application not found")
        if section not in application.setup_sections:
            raise ValueError("Unknown setup section")
        return await self.application_repo.update_section_status(application.id, section, completed)

    async def update_wizard_section(
        self,
        application_id: str,
        section: str,
        data: Dict[str, Any],
    ):
        """
        Update a specific wizard section with configuration data.
        Automatically marks the section as complete if data is valid.
        """
        application = await self.application_repo.get_by_application_id(application_id)
        if not application:
            raise ValueError("University application not found")
        
        if application.status in [
            UniversityApplicationStatusEnum.APPROVED,
            UniversityApplicationStatusEnum.ACTIVE,
            UniversityApplicationStatusEnum.PROVISIONING,
        ]:
            raise ValueError("Cannot edit an application after approval or activation")

        if section not in application.setup_sections:
            raise ValueError(f"Unknown setup section: {section}")

        # Map section names to field names in the document
        section_field_map = {
            "university_information": "university_information",
            "id_configuration": "id_configuration",
            "academic_years": "academic_year_configuration",
            "faculties": "faculties_configuration",
            "departments": "departments_configuration",
            "programmes": "programmes_configuration",
            "courses": "courses_configuration",
            "admission_cycle": "admission_cycle_configuration",
            "admission_categories": "admission_categories_configuration",
            "admission_requirements": "admission_requirements_configuration",
            "application_form": "application_form_configuration",
            "application_fee": "application_fee_configuration",
            "staff": "staff_setup_configuration",
            "role_permission": "role_permission_configuration",
            "student_id_configuration": "student_id_configuration",
            "staff_id_configuration": "staff_id_configuration",
            "applicant_id_configuration": "applicant_id_configuration",
            "hostel": "hostel_configuration",
            "finance": "finance_configuration",
            "library": "library_configuration",
            "grading": "grading_configuration",
            "graduation": "graduation_configuration",
            "module_enablement": "module_enablement",
        }

        field_name = section_field_map.get(section)
        if not field_name:
            raise ValueError(f"Unknown setup section: {section}")

        # Update the section and mark as complete
        update_data = {
            field_name: data,
            "setup_sections." + section: True,
            "updated_at": datetime.utcnow(),
        }

        # Use MongoDB dot notation for nested updates
        return await self.application_repo.update(application.id, update_data)

    async def submit_for_review(self, application_id: str):
        application = await self.application_repo.get_by_application_id(application_id)
        if not application:
            raise ValueError("University application not found")

        # Check mandatory sections using the completeness service
        can_submit, incomplete_mandatory = SetupCompletenessService.can_submit_for_review(application.setup_sections)
        if not can_submit:
            raise ValueError(f"Cannot submit application until all mandatory sections are complete: {', '.join(incomplete_mandatory)}")

        if application.status in [
            UniversityApplicationStatusEnum.SUBMITTED,
            UniversityApplicationStatusEnum.AWAITING_SUPER_ADMIN_APPROVAL,
            UniversityApplicationStatusEnum.APPROVED,
            UniversityApplicationStatusEnum.ACTIVE,
        ]:
            raise ValueError("Application has already been submitted or processed")

        updated = await self.application_repo.update(application.id, {
            "status": UniversityApplicationStatusEnum.AWAITING_SUPER_ADMIN_APPROVAL,
            "submitted_at": datetime.utcnow(),
            "review_requested_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        })
        
        # Notify super admins that application is ready for review
        try:
            uni_name = application.university_information.legal_name if application.university_information else "University"
            await notify_super_admins_for_application(
                tenant_id=None,
                title=f"New Application Review: {uni_name}",
                message=f"University setup application from {application.admin_email} is ready for review.",
                target_url="/admin/super-admin-review",
            )
        except Exception as e:
            # Log error but don't fail the submission
            import logging
            logging.getLogger(__name__).error(f"Failed to notify super admins: {e}")
        
        return updated

    async def approve_application(self, application_id: str, reviewer_id: str):
        application = await self.application_repo.get_by_application_id(application_id)
        if not application:
            raise ValueError("University application not found")
        if application.status != UniversityApplicationStatusEnum.AWAITING_SUPER_ADMIN_APPROVAL:
            raise ValueError("Application is not awaiting approval")

        uni_info = application.university_information
        if not uni_info:
            raise ValueError("University information not configured")

        # Single-university mode: do not create a distinct tenant record. The app operates
        # as one university deployment, so the tenant context is flattened to a single constant.
        updated_application = await self.application_repo.update(application.id, {
            "status": UniversityApplicationStatusEnum.PROVISIONING,
            "approved_at": datetime.utcnow(),
            "tenant_id": "single-university",
            "updated_at": datetime.utcnow(),
        })
        
        # Notify admin that application has been approved
        try:
            await notify_application_admin(
                admin_email=application.admin_email,
                title="Application Approved ✓",
                message=f"Your university setup application has been approved! Proceed to activate your university.",
                target_url="/admin/university-applications",
                tenant_id=application.tenant_id or "default",
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to notify admin of approval: {e}")
        
        return updated_application

    async def activate_application(self, application_id: str):
        application = await self.application_repo.get_by_application_id(application_id)
        if not application:
            raise ValueError("University application not found")
        if application.status != UniversityApplicationStatusEnum.PROVISIONING:
            raise ValueError("Application is not in provisioning stage")

        # Single-university mode: activation happens without creating or validating a separate tenant.
        return await self.application_repo.update(application.id, {
            "status": UniversityApplicationStatusEnum.ACTIVE,
            "activated_at": datetime.utcnow(),
            "tenant_id": "single-university",
            "updated_at": datetime.utcnow(),
        })

    async def reject_application(self, application_id: str, reviewer_id: str, reason: str):
        application = await self.application_repo.get_by_application_id(application_id)
        if not application:
            raise ValueError("University application not found")
        if application.status not in [
            UniversityApplicationStatusEnum.AWAITING_SUPER_ADMIN_APPROVAL,
            UniversityApplicationStatusEnum.PENDING_SETUP,
            UniversityApplicationStatusEnum.SUBMITTED,
        ]:
            raise ValueError("Application cannot be rejected in its current state")

        updated = await self.application_repo.update(application.id, {
            "status": UniversityApplicationStatusEnum.REJECTED,
            "review_notes": reason,
            "rejection_reason": reason,
            "rejected_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        })
        
        # Notify admin that application has been rejected
        try:
            await notify_application_admin(
                admin_email=application.admin_email,
                title="Application Rejected",
                message=f"Your university setup application was rejected. Reason: {reason}",
                target_url="/admin/university-applications",
                tenant_id=application.tenant_id,
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to notify admin of rejection: {e}")
        
        return updated

    def get_setup_completeness_summary(self, application) -> Dict[str, Any]:
        """Get a detailed summary of setup completeness."""
        return SetupCompletenessService.get_setup_summary(application.setup_sections)

    async def request_changes(self, application_id: str, reason: str):
        """
        Super admin requests changes to the application.
        Returns application to PENDING_SETUP so university admin can make corrections.
        """
        application = await self.application_repo.get_by_application_id(application_id)
        if not application:
            raise ValueError("University application not found")
        
        if application.status != UniversityApplicationStatusEnum.AWAITING_SUPER_ADMIN_APPROVAL:
            raise ValueError("Application is not awaiting super admin approval")

        updated = await self.application_repo.update(application.id, {
            "status": UniversityApplicationStatusEnum.PENDING_SETUP,
            "review_notes": reason,
            "updated_at": datetime.utcnow(),
        })
        
        # Notify admin that changes have been requested
        try:
            await notify_application_admin(
                admin_email=application.admin_email,
                title="Changes Requested",
                message=f"Super admin requested changes to your setup: {reason}",
                target_url="/admin/university-applications",
                tenant_id=application.tenant_id,
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to notify admin of change request: {e}")
        
        return updated
