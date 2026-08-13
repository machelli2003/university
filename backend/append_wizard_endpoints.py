#!/usr/bin/env python3
"""Script to append wizard endpoints to routes.py"""

wizard_code = """

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
"""

with open('app/presentation/api/v1/onboarding/routes.py', 'a') as f:
    f.write(wizard_code)

print("✓ Wizard endpoints appended successfully")
