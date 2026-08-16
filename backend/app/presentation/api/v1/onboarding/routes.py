from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List, Optional, Dict, Any
from app.presentation.api.v1.onboarding import schemas as onboarding_schemas
from app.application.onboarding.university_application_use_case import UniversityApplicationUseCase
from app.dependencies import (
    get_current_user, get_tenant_repo, get_university_application_repo,
    get_identifier_service, get_audit_repo, require_roles
)
from app.infrastructure.models.user import User
from app.infrastructure.models.university_application import UniversityApplicationStatusEnum
from app.domain.onboarding.setup_completeness_service import SetupCompletenessService

router = APIRouter()

@router.post("/applications", response_model=onboarding_schemas.UniversityApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_university_application(
    request: onboarding_schemas.CreateUniversityApplicationRequest,
    current_user: User = Depends(require_roles(["super_admin", "university_admin", "admin"])),
    application_repo=Depends(get_university_application_repo),
    tenant_repo=Depends(get_tenant_repo),
    identifier_service=Depends(get_identifier_service),
    audit_repo=Depends(get_audit_repo),
):
    use_case = UniversityApplicationUseCase(application_repo, tenant_repo, identifier_service)
    try:
        application = await use_case.create_application(
            legal_name=request.legal_name,
            display_name=request.display_name,
            school_code=request.school_code,
            requested_by=str(current_user.id),
            admin_first_name=request.admin_first_name,
            admin_last_name=request.admin_last_name,
            admin_email=request.admin_email,
            **request.dict(exclude={"legal_name", "display_name", "school_code", "admin_first_name", "admin_last_name", "admin_email"}),
        )
        await audit_repo.create({
            "tenant_id": None,
            "event_type": "university_application_created",
            "entity_type": "university_application",
            "entity_id": str(application.id),
            "action": "create_university_application",
            "performed_by": str(current_user.id),
            "details": {"university_application_id": application.university_application_id},
        })
        return onboarding_schemas.UniversityApplicationResponse.from_orm(application)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

@router.get("/applications", response_model=List[onboarding_schemas.UniversityApplicationResponse])
async def list_university_applications(
    status: Optional[str] = None,
    current_user: User = Depends(require_roles(["super_admin", "university_admin", "admin"])),
    application_repo=Depends(get_university_application_repo),
):
    if status:
        applications = await application_repo.list_by_status(status)
    else:
        applications = await application_repo.get_all()
    return [onboarding_schemas.UniversityApplicationResponse.from_orm(app) for app in applications]

@router.get("/applications/{application_id}", response_model=onboarding_schemas.UniversityApplicationResponse)
async def get_university_application(
    application_id: str,
    current_user: User = Depends(get_current_user),
    application_repo=Depends(get_university_application_repo),
):
    application = await application_repo.get_by_application_id(application_id)
    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="University application not found")

    # Allow super_admin, original requester, or university_admin / designated admin
    user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    is_super_admin = user_role in ["super_admin", "superadmin"]
    is_original_requester = application.requested_by == str(current_user.id)
    is_designated_admin = (application.admin_email or "").strip().lower() == (current_user.email or "").strip().lower()
    is_tenant_admin = user_role in ["university_admin", "admin"] and (
        application.tenant_id is None 
        or current_user.tenant_id == application.tenant_id 
        or is_designated_admin
    )
    
    if not (is_super_admin or is_original_requester or is_tenant_admin or is_designated_admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return onboarding_schemas.UniversityApplicationResponse.from_orm(application)

@router.patch("/applications/{application_id}", response_model=onboarding_schemas.UniversityApplicationResponse)
async def update_university_application(
    application_id: str,
    request: onboarding_schemas.UpdateUniversityApplicationRequest,
    current_user: User = Depends(require_roles("super_admin", "university_admin", "admin")),
    application_repo=Depends(get_university_application_repo),
    tenant_repo=Depends(get_tenant_repo),
    identifier_service=Depends(get_identifier_service),
    audit_repo=Depends(get_audit_repo),
):
    use_case = UniversityApplicationUseCase(application_repo, tenant_repo, identifier_service)
    try:
        application = await use_case.update_application(application_id, request.dict(exclude_none=True))
        await audit_repo.create({
            "tenant_id": application.tenant_id,
            "event_type": "university_application_updated",
            "entity_type": "university_application",
            "entity_id": application_id,
            "action": "update_university_application",
            "performed_by": str(current_user.id),
            "details": request.dict(exclude_none=True),
        })
        return onboarding_schemas.UniversityApplicationResponse.from_orm(application)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

@router.post("/applications/{application_id}/submit", response_model=onboarding_schemas.UniversityApplicationResponse)
async def submit_university_application_for_review(
    application_id: str,
    current_user: User = Depends(get_current_user),
    application_repo=Depends(get_university_application_repo),
    tenant_repo=Depends(get_tenant_repo),
    identifier_service=Depends(get_identifier_service),
    audit_repo=Depends(get_audit_repo),
):
    # Authorization: super_admin, original requester, designated admin, or university_admin
    user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    application = await application_repo.get_by_application_id(application_id)
    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    is_super_admin = user_role in ["super_admin", "superadmin"]
    is_original_requester = application.requested_by == str(current_user.id)
    is_designated_admin = (application.admin_email or "").strip().lower() == (current_user.email or "").strip().lower()
    is_tenant_admin = user_role in ["university_admin", "admin"] and (
        application.tenant_id is None 
        or current_user.tenant_id == application.tenant_id 
        or is_designated_admin
    )

    if not (is_super_admin or is_original_requester or is_tenant_admin or is_designated_admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to submit this application")
    
    use_case = UniversityApplicationUseCase(application_repo, tenant_repo, identifier_service)
    try:
        application = await use_case.submit_for_review(application_id)
        await audit_repo.create({
            "tenant_id": application.tenant_id,
            "event_type": "university_application_submitted",
            "entity_type": "university_application",
            "entity_id": application_id,
            "action": "submit_university_application",
            "performed_by": str(current_user.id),
            "details": {},
        })
        return onboarding_schemas.UniversityApplicationResponse.from_orm(application)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

@router.post("/applications/{application_id}/approve", response_model=onboarding_schemas.UniversityApplicationResponse)
async def approve_university_application(
    application_id: str,
    current_user: User = Depends(require_roles("super_admin")),
    application_repo=Depends(get_university_application_repo),
    tenant_repo=Depends(get_tenant_repo),
    identifier_service=Depends(get_identifier_service),
    audit_repo=Depends(get_audit_repo),
):
    use_case = UniversityApplicationUseCase(application_repo, tenant_repo, identifier_service)
    try:
        application = await use_case.approve_application(application_id, str(current_user.id))
        await audit_repo.create({
            "tenant_id": application.tenant_id,
            "event_type": "university_application_approved",
            "entity_type": "university_application",
            "entity_id": application_id,
            "action": "approve_university_application",
            "performed_by": str(current_user.id),
            "details": {},
        })
        return onboarding_schemas.UniversityApplicationResponse.from_orm(application)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        import logging
        logging.getLogger(__name__).error(f"Error approving application {application_id}: {exc}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error approving application: {str(exc)}")

@router.post("/applications/{application_id}/reject", response_model=onboarding_schemas.UniversityApplicationResponse)
async def reject_university_application(
    application_id: str,
    request: onboarding_schemas.RejectUniversityApplicationRequest,
    current_user: User = Depends(require_roles("super_admin")),
    application_repo=Depends(get_university_application_repo),
    tenant_repo=Depends(get_tenant_repo),
    identifier_service=Depends(get_identifier_service),
    audit_repo=Depends(get_audit_repo),
):
    use_case = UniversityApplicationUseCase(application_repo, tenant_repo, identifier_service)
    try:
        application = await use_case.reject_application(application_id, str(current_user.id), request.reason)
        await audit_repo.create({
            "tenant_id": application.tenant_id,
            "event_type": "university_application_rejected",
            "entity_type": "university_application",
            "entity_id": application_id,
            "action": "reject_university_application",
            "performed_by": str(current_user.id),
            "details": {"reason": request.reason},
        })
        return onboarding_schemas.UniversityApplicationResponse.from_orm(application)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        import logging
        logging.getLogger(__name__).error(f"Error rejecting application {application_id}: {exc}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error rejecting application: {str(exc)}")

@router.patch("/applications/{application_id}/sections/{section}", response_model=onboarding_schemas.UniversityApplicationResponse)
async def update_application_setup_section(
    application_id: str,
    section: str,
    request: onboarding_schemas.UpdateSetupSectionRequest,
    current_user: User = Depends(require_roles("super_admin", "university_admin", "admin")),
    application_repo=Depends(get_university_application_repo),
    tenant_repo=Depends(get_tenant_repo),
    identifier_service=Depends(get_identifier_service),
    audit_repo=Depends(get_audit_repo),
):
    use_case = UniversityApplicationUseCase(application_repo, tenant_repo, identifier_service)
    try:
        application = await use_case.update_setup_section(application_id, section, request.completed)
        await audit_repo.create({
            "tenant_id": application.tenant_id,
            "event_type": "university_application_section_updated",
            "entity_type": "university_application",
            "entity_id": application_id,
            "action": "update_university_application_section",
            "performed_by": str(current_user.id),
            "details": {"section": section, "completed": request.completed},
        })
        return onboarding_schemas.UniversityApplicationResponse.from_orm(application)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

@router.post("/applications/{application_id}/activate", response_model=onboarding_schemas.UniversityApplicationResponse)
async def activate_university_application(
    application_id: str,
    current_user: User = Depends(require_roles("super_admin")),
    application_repo=Depends(get_university_application_repo),
    tenant_repo=Depends(get_tenant_repo),
    identifier_service=Depends(get_identifier_service),
    audit_repo=Depends(get_audit_repo),
):
    use_case = UniversityApplicationUseCase(application_repo, tenant_repo, identifier_service)
    try:
        application = await use_case.activate_application(application_id)
        await audit_repo.create({
            "tenant_id": application.tenant_id,
            "event_type": "university_application_activated",
            "entity_type": "university_application",
            "entity_id": application_id,
            "action": "activate_university_application",
            "performed_by": str(current_user.id),
            "details": {},
        })
        return onboarding_schemas.UniversityApplicationResponse.from_orm(application)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


# ==================== WIZARD ENDPOINTS ====================
# Step 1: University Information
@router.patch("/applications/{application_id}/wizard/university-information", response_model=onboarding_schemas.UniversityApplicationResponse)
async def update_university_information(
    application_id: str,
    request: onboarding_schemas.UpdateUniversityInformationRequest,
    current_user: User = Depends(get_current_user),
    application_repo=Depends(get_university_application_repo),
    tenant_repo=Depends(get_tenant_repo),
    identifier_service=Depends(get_identifier_service),
    audit_repo=Depends(get_audit_repo),
):
    use_case = UniversityApplicationUseCase(application_repo, tenant_repo, identifier_service)
    try:
        application = await use_case.update_wizard_section(
            application_id, "university_information", request.dict(exclude_none=True)
        )
        await audit_repo.create({
            "event_type": "university_information_updated",
            "entity_type": "university_application",
            "entity_id": application_id,
            "action": "update_university_information",
            "performed_by": str(current_user.id),
            "details": {"section": "university_information"},
        })
        return onboarding_schemas.UniversityApplicationResponse.from_orm(application)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


# Step 2: ID Configuration
@router.patch("/applications/{application_id}/wizard/id-configuration", response_model=onboarding_schemas.UniversityApplicationResponse)
async def update_id_configuration(
    application_id: str,
    request: onboarding_schemas.UpdateIDConfigurationRequest,
    current_user: User = Depends(get_current_user),
    application_repo=Depends(get_university_application_repo),
    tenant_repo=Depends(get_tenant_repo),
    identifier_service=Depends(get_identifier_service),
    audit_repo=Depends(get_audit_repo),
):
    use_case = UniversityApplicationUseCase(application_repo, tenant_repo, identifier_service)
    try:
        application = await use_case.update_wizard_section(
            application_id, "id_configuration", request.dict(exclude_none=True)
        )
        await audit_repo.create({
            "event_type": "id_configuration_updated",
            "entity_type": "university_application",
            "entity_id": application_id,
            "action": "update_id_configuration",
            "performed_by": str(current_user.id),
            "details": {"section": "id_configuration"},
        })
        return onboarding_schemas.UniversityApplicationResponse.from_orm(application)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

# Step 3-23: remaining setup sections
@router.patch("/applications/{application_id}/wizard/academic-years", response_model=onboarding_schemas.UniversityApplicationResponse)
async def update_academic_years(
    application_id: str,
    request: onboarding_schemas.UpdateAcademicYearConfigurationRequest,
    current_user: User = Depends(get_current_user),
    application_repo=Depends(get_university_application_repo),
    tenant_repo=Depends(get_tenant_repo),
    identifier_service=Depends(get_identifier_service),
    audit_repo=Depends(get_audit_repo),
):
    use_case = UniversityApplicationUseCase(application_repo, tenant_repo, identifier_service)
    try:
        application = await use_case.update_wizard_section(application_id, "academic_years", request.dict(exclude_none=True))
        await audit_repo.create({"event_type": "academic_years_updated", "entity_type": "university_application", "entity_id": application_id, "action": "update_academic_years", "performed_by": str(current_user.id), "details": {"section": "academic_years"}})
        return onboarding_schemas.UniversityApplicationResponse.from_orm(application)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

@router.patch("/applications/{application_id}/wizard/faculties", response_model=onboarding_schemas.UniversityApplicationResponse)
async def update_faculties(
    application_id: str,
    request: onboarding_schemas.UpdateFacultiesConfigurationRequest,
    current_user: User = Depends(get_current_user),
    application_repo=Depends(get_university_application_repo),
    tenant_repo=Depends(get_tenant_repo),
    identifier_service=Depends(get_identifier_service),
    audit_repo=Depends(get_audit_repo),
):
    use_case = UniversityApplicationUseCase(application_repo, tenant_repo, identifier_service)
    try:
        application = await use_case.update_wizard_section(application_id, "faculties", request.dict(exclude_none=True))
        await audit_repo.create({"event_type": "faculties_updated", "entity_type": "university_application", "entity_id": application_id, "action": "update_faculties", "performed_by": str(current_user.id), "details": {"section": "faculties"}})
        return onboarding_schemas.UniversityApplicationResponse.from_orm(application)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

@router.patch("/applications/{application_id}/wizard/departments", response_model=onboarding_schemas.UniversityApplicationResponse)
async def update_departments(
    application_id: str,
    request: onboarding_schemas.UpdateDepartmentsConfigurationRequest,
    current_user: User = Depends(get_current_user),
    application_repo=Depends(get_university_application_repo),
    tenant_repo=Depends(get_tenant_repo),
    identifier_service=Depends(get_identifier_service),
    audit_repo=Depends(get_audit_repo),
):
    use_case = UniversityApplicationUseCase(application_repo, tenant_repo, identifier_service)
    try:
        application = await use_case.update_wizard_section(application_id, "departments", request.dict(exclude_none=True))
        await audit_repo.create({"event_type": "departments_updated", "entity_type": "university_application", "entity_id": application_id, "action": "update_departments", "performed_by": str(current_user.id), "details": {"section": "departments"}})
        return onboarding_schemas.UniversityApplicationResponse.from_orm(application)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

@router.patch("/applications/{application_id}/wizard/programmes", response_model=onboarding_schemas.UniversityApplicationResponse)
async def update_programmes(
    application_id: str,
    request: onboarding_schemas.UpdateProgrammesConfigurationRequest,
    current_user: User = Depends(get_current_user),
    application_repo=Depends(get_university_application_repo),
    tenant_repo=Depends(get_tenant_repo),
    identifier_service=Depends(get_identifier_service),
    audit_repo=Depends(get_audit_repo),
):
    use_case = UniversityApplicationUseCase(application_repo, tenant_repo, identifier_service)
    try:
        application = await use_case.update_wizard_section(application_id, "programmes", request.dict(exclude_none=True))
        await audit_repo.create({"event_type": "programmes_updated", "entity_type": "university_application", "entity_id": application_id, "action": "update_programmes", "performed_by": str(current_user.id), "details": {"section": "programmes"}})
        return onboarding_schemas.UniversityApplicationResponse.from_orm(application)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

@router.patch("/applications/{application_id}/wizard/courses", response_model=onboarding_schemas.UniversityApplicationResponse)
async def update_courses(
    application_id: str,
    request: onboarding_schemas.UpdateCoursesConfigurationRequest,
    current_user: User = Depends(get_current_user),
    application_repo=Depends(get_university_application_repo),
    tenant_repo=Depends(get_tenant_repo),
    identifier_service=Depends(get_identifier_service),
    audit_repo=Depends(get_audit_repo),
):
    use_case = UniversityApplicationUseCase(application_repo, tenant_repo, identifier_service)
    try:
        application = await use_case.update_wizard_section(application_id, "courses", request.dict(exclude_none=True))
        await audit_repo.create({"event_type": "courses_updated", "entity_type": "university_application", "entity_id": application_id, "action": "update_courses", "performed_by": str(current_user.id), "details": {"section": "courses"}})
        return onboarding_schemas.UniversityApplicationResponse.from_orm(application)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

@router.patch("/applications/{application_id}/wizard/admission-cycle", response_model=onboarding_schemas.UniversityApplicationResponse)
async def update_admission_cycle(
    application_id: str,
    request: onboarding_schemas.UpdateAdmissionCycleConfigurationRequest,
    current_user: User = Depends(get_current_user),
    application_repo=Depends(get_university_application_repo),
    tenant_repo=Depends(get_tenant_repo),
    identifier_service=Depends(get_identifier_service),
    audit_repo=Depends(get_audit_repo),
):
    use_case = UniversityApplicationUseCase(application_repo, tenant_repo, identifier_service)
    try:
        application = await use_case.update_wizard_section(application_id, "admission_cycle", request.dict(exclude_none=True))
        await audit_repo.create({"event_type": "admission_cycle_updated", "entity_type": "university_application", "entity_id": application_id, "action": "update_admission_cycle", "performed_by": str(current_user.id), "details": {"section": "admission_cycle"}})
        return onboarding_schemas.UniversityApplicationResponse.from_orm(application)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

@router.patch("/applications/{application_id}/wizard/admission-categories", response_model=onboarding_schemas.UniversityApplicationResponse)
async def update_admission_categories(
    application_id: str,
    request: onboarding_schemas.UpdateAdmissionCategoriesConfigurationRequest,
    current_user: User = Depends(get_current_user),
    application_repo=Depends(get_university_application_repo),
    tenant_repo=Depends(get_tenant_repo),
    identifier_service=Depends(get_identifier_service),
    audit_repo=Depends(get_audit_repo),
):
    use_case = UniversityApplicationUseCase(application_repo, tenant_repo, identifier_service)
    try:
        application = await use_case.update_wizard_section(application_id, "admission_categories", request.dict(exclude_none=True))
        await audit_repo.create({"event_type": "admission_categories_updated", "entity_type": "university_application", "entity_id": application_id, "action": "update_admission_categories", "performed_by": str(current_user.id), "details": {"section": "admission_categories"}})
        return onboarding_schemas.UniversityApplicationResponse.from_orm(application)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

@router.patch("/applications/{application_id}/wizard/admission-requirements", response_model=onboarding_schemas.UniversityApplicationResponse)
async def update_admission_requirements(
    application_id: str,
    request: onboarding_schemas.UpdateAdmissionRequirementsConfigurationRequest,
    current_user: User = Depends(get_current_user),
    application_repo=Depends(get_university_application_repo),
    tenant_repo=Depends(get_tenant_repo),
    identifier_service=Depends(get_identifier_service),
    audit_repo=Depends(get_audit_repo),
):
    use_case = UniversityApplicationUseCase(application_repo, tenant_repo, identifier_service)
    try:
        application = await use_case.update_wizard_section(application_id, "admission_requirements", request.dict(exclude_none=True))
        await audit_repo.create({"event_type": "admission_requirements_updated", "entity_type": "university_application", "entity_id": application_id, "action": "update_admission_requirements", "performed_by": str(current_user.id), "details": {"section": "admission_requirements"}})
        return onboarding_schemas.UniversityApplicationResponse.from_orm(application)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

@router.patch("/applications/{application_id}/wizard/application-form", response_model=onboarding_schemas.UniversityApplicationResponse)
async def update_application_form(
    application_id: str,
    request: onboarding_schemas.UpdateApplicationFormConfigurationRequest,
    current_user: User = Depends(get_current_user),
    application_repo=Depends(get_university_application_repo),
    tenant_repo=Depends(get_tenant_repo),
    identifier_service=Depends(get_identifier_service),
    audit_repo=Depends(get_audit_repo),
):
    use_case = UniversityApplicationUseCase(application_repo, tenant_repo, identifier_service)
    try:
        application = await use_case.update_wizard_section(application_id, "application_form", request.dict(exclude_none=True))
        await audit_repo.create({"event_type": "application_form_updated", "entity_type": "university_application", "entity_id": application_id, "action": "update_application_form", "performed_by": str(current_user.id), "details": {"section": "application_form"}})
        return onboarding_schemas.UniversityApplicationResponse.from_orm(application)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

@router.patch("/applications/{application_id}/wizard/application-fee", response_model=onboarding_schemas.UniversityApplicationResponse)
async def update_application_fee(
    application_id: str,
    request: onboarding_schemas.UpdateApplicationFeeConfigurationRequest,
    current_user: User = Depends(get_current_user),
    application_repo=Depends(get_university_application_repo),
    tenant_repo=Depends(get_tenant_repo),
    identifier_service=Depends(get_identifier_service),
    audit_repo=Depends(get_audit_repo),
):
    use_case = UniversityApplicationUseCase(application_repo, tenant_repo, identifier_service)
    try:
        application = await use_case.update_wizard_section(application_id, "application_fee", request.dict(exclude_none=True))
        await audit_repo.create({"event_type": "application_fee_updated", "entity_type": "university_application", "entity_id": application_id, "action": "update_application_fee", "performed_by": str(current_user.id), "details": {"section": "application_fee"}})
        return onboarding_schemas.UniversityApplicationResponse.from_orm(application)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

@router.patch("/applications/{application_id}/wizard/staff", response_model=onboarding_schemas.UniversityApplicationResponse)
async def update_staff(
    application_id: str,
    request: onboarding_schemas.UpdateStaffSetupConfigurationRequest,
    current_user: User = Depends(get_current_user),
    application_repo=Depends(get_university_application_repo),
    tenant_repo=Depends(get_tenant_repo),
    identifier_service=Depends(get_identifier_service),
    audit_repo=Depends(get_audit_repo),
):
    use_case = UniversityApplicationUseCase(application_repo, tenant_repo, identifier_service)
    try:
        application = await use_case.update_wizard_section(application_id, "staff", request.dict(exclude_none=True))
        await audit_repo.create({"event_type": "staff_updated", "entity_type": "university_application", "entity_id": application_id, "action": "update_staff", "performed_by": str(current_user.id), "details": {"section": "staff"}})
        return onboarding_schemas.UniversityApplicationResponse.from_orm(application)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

@router.patch("/applications/{application_id}/wizard/student-id-configuration", response_model=onboarding_schemas.UniversityApplicationResponse)
async def update_student_id_configuration(
    application_id: str,
    request: onboarding_schemas.UpdateStudentIDConfigurationRequest,
    current_user: User = Depends(get_current_user),
    application_repo=Depends(get_university_application_repo),
    tenant_repo=Depends(get_tenant_repo),
    identifier_service=Depends(get_identifier_service),
    audit_repo=Depends(get_audit_repo),
):
    use_case = UniversityApplicationUseCase(application_repo, tenant_repo, identifier_service)
    try:
        application = await use_case.update_wizard_section(application_id, "student_id_configuration", request.dict(exclude_none=True))
        await audit_repo.create({"event_type": "student_id_configuration_updated", "entity_type": "university_application", "entity_id": application_id, "action": "update_student_id_configuration", "performed_by": str(current_user.id), "details": {"section": "student_id_configuration"}})
        return onboarding_schemas.UniversityApplicationResponse.from_orm(application)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

@router.patch("/applications/{application_id}/wizard/staff-id-configuration", response_model=onboarding_schemas.UniversityApplicationResponse)
async def update_staff_id_configuration(
    application_id: str,
    request: onboarding_schemas.UpdateStaffIDConfigurationRequest,
    current_user: User = Depends(get_current_user),
    application_repo=Depends(get_university_application_repo),
    tenant_repo=Depends(get_tenant_repo),
    identifier_service=Depends(get_identifier_service),
    audit_repo=Depends(get_audit_repo),
):
    use_case = UniversityApplicationUseCase(application_repo, tenant_repo, identifier_service)
    try:
        application = await use_case.update_wizard_section(application_id, "staff_id_configuration", request.dict(exclude_none=True))
        await audit_repo.create({"event_type": "staff_id_configuration_updated", "entity_type": "university_application", "entity_id": application_id, "action": "update_staff_id_configuration", "performed_by": str(current_user.id), "details": {"section": "staff_id_configuration"}})
        return onboarding_schemas.UniversityApplicationResponse.from_orm(application)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

@router.patch("/applications/{application_id}/wizard/applicant-id-configuration", response_model=onboarding_schemas.UniversityApplicationResponse)
async def update_applicant_id_configuration(
    application_id: str,
    request: onboarding_schemas.UpdateApplicantIDConfigurationRequest,
    current_user: User = Depends(get_current_user),
    application_repo=Depends(get_university_application_repo),
    tenant_repo=Depends(get_tenant_repo),
    identifier_service=Depends(get_identifier_service),
    audit_repo=Depends(get_audit_repo),
):
    use_case = UniversityApplicationUseCase(application_repo, tenant_repo, identifier_service)
    try:
        application = await use_case.update_wizard_section(application_id, "applicant_id_configuration", request.dict(exclude_none=True))
        await audit_repo.create({"event_type": "applicant_id_configuration_updated", "entity_type": "university_application", "entity_id": application_id, "action": "update_applicant_id_configuration", "performed_by": str(current_user.id), "details": {"section": "applicant_id_configuration"}})
        return onboarding_schemas.UniversityApplicationResponse.from_orm(application)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

@router.patch("/applications/{application_id}/wizard/finance", response_model=onboarding_schemas.UniversityApplicationResponse)
async def update_finance(
    application_id: str,
    request: onboarding_schemas.UpdateFinanceConfigurationRequest,
    current_user: User = Depends(get_current_user),
    application_repo=Depends(get_university_application_repo),
    tenant_repo=Depends(get_tenant_repo),
    identifier_service=Depends(get_identifier_service),
    audit_repo=Depends(get_audit_repo),
):
    use_case = UniversityApplicationUseCase(application_repo, tenant_repo, identifier_service)
    try:
        application = await use_case.update_wizard_section(application_id, "finance", request.dict(exclude_none=True))
        await audit_repo.create({"event_type": "finance_updated", "entity_type": "university_application", "entity_id": application_id, "action": "update_finance", "performed_by": str(current_user.id), "details": {"section": "finance"}})
        return onboarding_schemas.UniversityApplicationResponse.from_orm(application)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

@router.patch("/applications/{application_id}/wizard/grading", response_model=onboarding_schemas.UniversityApplicationResponse)
async def update_grading(
    application_id: str,
    request: onboarding_schemas.UpdateGradingConfigurationRequest,
    current_user: User = Depends(get_current_user),
    application_repo=Depends(get_university_application_repo),
    tenant_repo=Depends(get_tenant_repo),
    identifier_service=Depends(get_identifier_service),
    audit_repo=Depends(get_audit_repo),
):
    use_case = UniversityApplicationUseCase(application_repo, tenant_repo, identifier_service)
    try:
        application = await use_case.update_wizard_section(application_id, "grading", request.dict(exclude_none=True))
        await audit_repo.create({"event_type": "grading_updated", "entity_type": "university_application", "entity_id": application_id, "action": "update_grading", "performed_by": str(current_user.id), "details": {"section": "grading"}})
        return onboarding_schemas.UniversityApplicationResponse.from_orm(application)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

@router.patch("/applications/{application_id}/wizard/graduation", response_model=onboarding_schemas.UniversityApplicationResponse)
async def update_graduation(
    application_id: str,
    request: onboarding_schemas.UpdateGraduationConfigurationRequest,
    current_user: User = Depends(get_current_user),
    application_repo=Depends(get_university_application_repo),
    tenant_repo=Depends(get_tenant_repo),
    identifier_service=Depends(get_identifier_service),
    audit_repo=Depends(get_audit_repo),
):
    use_case = UniversityApplicationUseCase(application_repo, tenant_repo, identifier_service)
    try:
        application = await use_case.update_wizard_section(application_id, "graduation", request.dict(exclude_none=True))
        await audit_repo.create({"event_type": "graduation_updated", "entity_type": "university_application", "entity_id": application_id, "action": "update_graduation", "performed_by": str(current_user.id), "details": {"section": "graduation"}})
        return onboarding_schemas.UniversityApplicationResponse.from_orm(application)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

@router.patch("/applications/{application_id}/wizard/module-enablement", response_model=onboarding_schemas.UniversityApplicationResponse)
async def update_module_enablement(
    application_id: str,
    request: onboarding_schemas.UpdateModuleEnablementRequest,
    current_user: User = Depends(get_current_user),
    application_repo=Depends(get_university_application_repo),
    tenant_repo=Depends(get_tenant_repo),
    identifier_service=Depends(get_identifier_service),
    audit_repo=Depends(get_audit_repo),
):
    use_case = UniversityApplicationUseCase(application_repo, tenant_repo, identifier_service)
    try:
        application = await use_case.update_wizard_section(application_id, "module_enablement", request.dict(exclude_none=True))
        await audit_repo.create({"event_type": "module_enablement_updated", "entity_type": "university_application", "entity_id": application_id, "action": "update_module_enablement", "performed_by": str(current_user.id), "details": {"section": "module_enablement"}})
        return onboarding_schemas.UniversityApplicationResponse.from_orm(application)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

@router.patch("/applications/{application_id}/wizard/role-permission", response_model=onboarding_schemas.UniversityApplicationResponse)
async def update_role_permission(
    application_id: str,
    request: onboarding_schemas.UpdateRolePermissionConfigurationRequest,
    current_user: User = Depends(get_current_user),
    application_repo=Depends(get_university_application_repo),
    tenant_repo=Depends(get_tenant_repo),
    identifier_service=Depends(get_identifier_service),
    audit_repo=Depends(get_audit_repo),
):
    use_case = UniversityApplicationUseCase(application_repo, tenant_repo, identifier_service)
    try:
        application = await use_case.update_wizard_section(application_id, "role_permission", request.dict(exclude_none=True))
        await audit_repo.create({"event_type": "role_permission_updated", "entity_type": "university_application", "entity_id": application_id, "action": "update_role_permission", "performed_by": str(current_user.id), "details": {"section": "role_permission"}})
        return onboarding_schemas.UniversityApplicationResponse.from_orm(application)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

@router.patch("/applications/{application_id}/wizard/hostel-configuration", response_model=onboarding_schemas.UniversityApplicationResponse)
async def update_hostel_configuration(
    application_id: str,
    request: onboarding_schemas.UpdateHostelConfigurationRequest,
    current_user: User = Depends(get_current_user),
    application_repo=Depends(get_university_application_repo),
    tenant_repo=Depends(get_tenant_repo),
    identifier_service=Depends(get_identifier_service),
    audit_repo=Depends(get_audit_repo),
):
    use_case = UniversityApplicationUseCase(application_repo, tenant_repo, identifier_service)
    try:
        application = await use_case.update_wizard_section(application_id, "hostel", request.dict(exclude_none=True))
        await audit_repo.create({"event_type": "hostel_configuration_updated", "entity_type": "university_application", "entity_id": application_id, "action": "update_hostel_configuration", "performed_by": str(current_user.id), "details": {"section": "hostel"}})
        return onboarding_schemas.UniversityApplicationResponse.from_orm(application)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

@router.patch("/applications/{application_id}/wizard/library-configuration", response_model=onboarding_schemas.UniversityApplicationResponse)
async def update_library_configuration(
    application_id: str,
    request: onboarding_schemas.UpdateLibraryConfigurationRequest,
    current_user: User = Depends(get_current_user),
    application_repo=Depends(get_university_application_repo),
    tenant_repo=Depends(get_tenant_repo),
    identifier_service=Depends(get_identifier_service),
    audit_repo=Depends(get_audit_repo),
):
    use_case = UniversityApplicationUseCase(application_repo, tenant_repo, identifier_service)
    try:
        application = await use_case.update_wizard_section(application_id, "library", request.dict(exclude_none=True))
        await audit_repo.create({"event_type": "library_configuration_updated", "entity_type": "university_application", "entity_id": application_id, "action": "update_library_configuration", "performed_by": str(current_user.id), "details": {"section": "library"}})
        return onboarding_schemas.UniversityApplicationResponse.from_orm(application)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

# Setup Completeness & University Admin Review
@router.get("/applications/{application_id}/setup-completeness", status_code=status.HTTP_200_OK)
async def get_setup_completeness(
    application_id: str,
    current_user: User = Depends(get_current_user),
    application_repo=Depends(get_university_application_repo),
):
    application = await application_repo.get_by_application_id(application_id)
    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="University application not found")

    if current_user.role.value != "super_admin" and application.requested_by != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    completeness_summary = SetupCompletenessService.get_setup_summary(application.setup_sections)
    return {
        "application_id": application.university_application_id,
        "status": application.status,
        "completeness": completeness_summary,
    }



# ==================== SUPER ADMIN REVIEW ENDPOINTS (Sections 30-32) ====================

# Get applications awaiting super admin review
@router.get("/applications/review/pending", response_model=List[onboarding_schemas.UniversityApplicationResponse])
async def get_pending_review_applications(
    current_user: User = Depends(require_roles("super_admin")),
    application_repo=Depends(get_university_application_repo),
):
    applications = await application_repo.list_by_status("awaiting_super_admin_approval")
    return [onboarding_schemas.UniversityApplicationResponse.from_orm(app) for app in applications]


# Get all applications (super admin dashboard)
@router.get("/applications/review/all", response_model=List[onboarding_schemas.UniversityApplicationResponse])
async def get_all_applications_for_review(
    status: Optional[str] = None,
    current_user: User = Depends(require_roles("super_admin")),
    application_repo=Depends(get_university_application_repo),
):
    if status:
        applications = await application_repo.list_by_status(status)
    else:
        applications = await application_repo.get_all()
    return [onboarding_schemas.UniversityApplicationResponse.from_orm(app) for app in applications]


# Get review details for super admin (includes completeness)
@router.get("/applications/{application_id}/review-details", status_code=status.HTTP_200_OK)
async def get_application_review_details(
    application_id: str,
    current_user: User = Depends(require_roles("super_admin")),
    application_repo=Depends(get_university_application_repo),
    tenant_repo=Depends(get_tenant_repo),
    identifier_service=Depends(get_identifier_service),
):
    application = await application_repo.get_by_application_id(application_id)
    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="University application not found")

    use_case = UniversityApplicationUseCase(application_repo, tenant_repo, identifier_service)
    completeness_summary = use_case.get_setup_completeness_summary(application)
    
    return {
        "application": onboarding_schemas.UniversityApplicationResponse.from_orm(application),
        "completeness": completeness_summary,
        "can_approve": completeness_summary["can_submit_for_review"],  # Admin can only approve if all mandatory sections complete
    }


# Super admin approves application
@router.post("/applications/{application_id}/review/approve", response_model=onboarding_schemas.UniversityApplicationResponse)
async def approve_application_for_super_admin(
    application_id: str,
    request: onboarding_schemas.ApproveUniversityApplicationRequest,
    current_user: User = Depends(require_roles("super_admin")),
    application_repo=Depends(get_university_application_repo),
    tenant_repo=Depends(get_tenant_repo),
    identifier_service=Depends(get_identifier_service),
    audit_repo=Depends(get_audit_repo),
):
    use_case = UniversityApplicationUseCase(application_repo, tenant_repo, identifier_service)
    try:
        application = await use_case.approve_application(application_id, str(current_user.id))
        await audit_repo.create({
            "tenant_id": application.tenant_id,
            "event_type": "university_application_approved",
            "entity_type": "university_application",
            "entity_id": application_id,
            "action": "approve_university_application",
            "performed_by": str(current_user.id),
            "actor_type": "super_admin",
            "details": {"approval_notes": request.approval_notes},
        })
        return onboarding_schemas.UniversityApplicationResponse.from_orm(application)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


# Super admin rejects application
@router.post("/applications/{application_id}/review/reject", response_model=onboarding_schemas.UniversityApplicationResponse)
async def reject_application_from_review(
    application_id: str,
    request: onboarding_schemas.RejectUniversityApplicationRequest,
    current_user: User = Depends(require_roles("super_admin")),
    application_repo=Depends(get_university_application_repo),
    tenant_repo=Depends(get_tenant_repo),
    identifier_service=Depends(get_identifier_service),
    audit_repo=Depends(get_audit_repo),
):
    use_case = UniversityApplicationUseCase(application_repo, tenant_repo, identifier_service)
    try:
        application = await use_case.reject_application(application_id, str(current_user.id), request.reason)
        await audit_repo.create({
            "tenant_id": application.tenant_id,
            "event_type": "university_application_rejected",
            "entity_type": "university_application",
            "entity_id": application_id,
            "action": "reject_university_application",
            "performed_by": str(current_user.id),
            "actor_type": "super_admin",
            "details": {"reason": request.reason},
        })
        return onboarding_schemas.UniversityApplicationResponse.from_orm(application)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


# Super admin requests changes to application
@router.post("/applications/{application_id}/review/request-changes", response_model=onboarding_schemas.UniversityApplicationResponse)
async def request_application_changes_from_super_admin(
    application_id: str,
    request: onboarding_schemas.RequestUniversityApplicationChangesRequest,
    current_user: User = Depends(require_roles("super_admin")),
    application_repo=Depends(get_university_application_repo),
    tenant_repo=Depends(get_tenant_repo),
    identifier_service=Depends(get_identifier_service),
    audit_repo=Depends(get_audit_repo),
):
    use_case = UniversityApplicationUseCase(application_repo, tenant_repo, identifier_service)
    try:
        application = await use_case.request_changes(application_id, request.reason)
        await audit_repo.create({
            "tenant_id": application.tenant_id,
            "event_type": "university_application_changes_requested",
            "entity_type": "university_application",
            "entity_id": application_id,
            "action": "request_application_changes",
            "performed_by": str(current_user.id),
            "actor_type": "super_admin",
            "details": {"reason": request.reason},
        })
        return onboarding_schemas.UniversityApplicationResponse.from_orm(application)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        import logging
        logging.getLogger(__name__).error(f"Error requesting changes for application {application_id}: {exc}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error requesting changes: {str(exc)}")


# Activate approved application (transition from PROVISIONING to ACTIVE)
@router.post("/applications/{application_id}/review/activate", response_model=onboarding_schemas.UniversityApplicationResponse)
async def activate_approved_application(
    application_id: str,
    current_user: User = Depends(require_roles("super_admin")),
    application_repo=Depends(get_university_application_repo),
    tenant_repo=Depends(get_tenant_repo),
    identifier_service=Depends(get_identifier_service),
    audit_repo=Depends(get_audit_repo),
):
    use_case = UniversityApplicationUseCase(application_repo, tenant_repo, identifier_service)
    try:
        application = await use_case.activate_application(application_id)
        await audit_repo.create({
            "tenant_id": application.tenant_id,
            "event_type": "university_activated",
            "entity_type": "university_application",
            "entity_id": application_id,
            "action": "activate_university",
            "performed_by": str(current_user.id),
            "actor_type": "super_admin",
            "details": {"message": "University activated and admissions portal is now live"},
        })
        return onboarding_schemas.UniversityApplicationResponse.from_orm(application)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
