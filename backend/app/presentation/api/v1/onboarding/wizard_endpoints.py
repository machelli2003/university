

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

    # Allow super_admin, original requester, or university_admin accessing their own tenant
    user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    is_super_admin = user_role in ["super_admin", "superadmin"]
    is_original_requester = application.requested_by == str(current_user.id)
    is_tenant_admin = user_role in ["university_admin", "admin"] and (
        application.tenant_id is None 
        or current_user.tenant_id == application.tenant_id
    )
    
    if not (is_super_admin or is_original_requester or is_tenant_admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    completeness_summary = SetupCompletenessService.get_setup_summary(application.setup_sections)
    return {
        "application_id": application.university_application_id,
        "status": application.status,
        "completeness": completeness_summary,
    }
