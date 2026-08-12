from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from datetime import datetime
from app.presentation.api.v1.alumni.schemas import (
    CreateAlumniProfileRequest, RequestMentorshipRequest, MakeDonationRequest
)
from app.infrastructure.database.repositories.alumni_repository import (
    AlumniProfileRepository, MentorshipRepository, DonationRepository
)
from app.dependencies import get_current_user, require_roles
from app.infrastructure.models.user import User

router = APIRouter()

def get_alumni_repo() -> AlumniProfileRepository:
    return AlumniProfileRepository()

def get_mentorship_repo() -> MentorshipRepository:
    return MentorshipRepository()

def get_donation_repo() -> DonationRepository:
    return DonationRepository()

@router.post("/profiles")
async def create_alumni_profile(
    request: CreateAlumniProfileRequest,
    current_user: User = Depends(get_current_user),
    alumni_repo=Depends(get_alumni_repo),
):
    profile = await alumni_repo.create({"tenant_id": current_user.tenant_id or "default", **request.dict()})
    return {"id": str(profile.id)}

@router.get("/directory")
async def get_alumni_directory(
    graduation_year: int = None,
    current_user: User = Depends(get_current_user),
    alumni_repo=Depends(get_alumni_repo),
):
    tenant_id = current_user.tenant_id or "default"
    if graduation_year:
        profiles = await alumni_repo.get_by_graduation_year(tenant_id, graduation_year)
    else:
        profiles = await alumni_repo.get_all(tenant_id=tenant_id)
    return [
        {"id": str(p.id), "current_occupation": p.current_occupation, "company": p.company}
        for p in profiles
    ]

@router.post("/mentorship/request")
async def request_mentorship(
    request: RequestMentorshipRequest,
    current_user: User = Depends(get_current_user),
    mentorship_repo=Depends(get_mentorship_repo),
):
    mentorship = await mentorship_repo.create({
        "tenant_id": current_user.tenant_id or "default",
        "mentor_id": request.mentor_id,
        "mentee_id": str(current_user.id),
        "start_date": datetime.utcnow(),
    })
    return {"id": str(mentorship.id), "status": "active"}

@router.post("/donations")
async def make_donation(
    request: MakeDonationRequest,
    current_user: User = Depends(get_current_user),
    donation_repo=Depends(get_donation_repo),
):
    donation = await donation_repo.create({
        "tenant_id": current_user.tenant_id or "default",
        "donor_id": str(current_user.id),
        "donation_date": datetime.utcnow(),
        **request.dict()
    })
    return {"id": str(donation.id)}

@router.get("/donations/total")
async def get_total_donations(
    current_user: User = Depends(require_roles("university_admin", "super_admin")),
    donation_repo=Depends(get_donation_repo),
):
    total = await donation_repo.get_total_for_tenant(current_user.tenant_id or "default")
    return {"total_donations": total}
