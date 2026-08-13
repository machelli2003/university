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
    current_user: User = Depends(require_roles("super_admin")),
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
    current_user: User = Depends(require_roles("super_admin", "university_admin")),
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

    if current_user.role.value != "super_admin" and application.requested_by != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return onboarding_schemas.UniversityApplicationResponse.from_orm(application)

@router.patch("/applications/{application_id}", response_model=onboarding_schemas.UniversityApplicationResponse)
async def update_university_application(
    application_id: str,
    request: onboarding_schemas.UpdateUniversityApplicationRequest,
    current_user: User = Depends(require_roles("super_admin")),
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
    current_user: User = Depends(require_roles("super_admin")),
    application_repo=Depends(get_university_application_repo),
    tenant_repo=Depends(get_tenant_repo),
    identifier_service=Depends(get_identifier_service),
    audit_repo=Depends(get_audit_repo),
):
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

@router.patch("/applications/{application_id}/sections/{section}", response_model=onboarding_schemas.UniversityApplicationResponse)
async def update_application_setup_section(
    application_id: str,
    section: str,
    request: onboarding_schemas.UpdateSetupSectionRequest,
    current_user: User = Depends(require_roles("super_admin")),
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
            "performed_by": str(current_user.id),
        })
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
