#!/usr/bin/env python3
"""Script to append super admin endpoints to routes.py"""

super_admin_code = """


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
"""

with open('app/presentation/api/v1/onboarding/routes.py', 'a') as f:
    f.write(super_admin_code)

print("✓ Super admin review endpoints appended successfully")
