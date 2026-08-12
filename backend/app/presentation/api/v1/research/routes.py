from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from app.presentation.api.v1.research.schemas import (
    CreateProposalRequest, CreateGrantRequest, CreatePublicationRequest
)
from app.infrastructure.database.repositories.research_repository import (
    ResearchProposalRepository, GrantRepository, PublicationRepository
)
from app.dependencies import get_current_user, require_roles
from app.infrastructure.models.user import User

router = APIRouter()

def get_proposal_repo() -> ResearchProposalRepository:
    return ResearchProposalRepository()

def get_grant_repo() -> GrantRepository:
    return GrantRepository()

def get_publication_repo() -> PublicationRepository:
    return PublicationRepository()

@router.post("/proposals")
async def create_proposal(
    request: CreateProposalRequest,
    current_user: User = Depends(require_roles("lecturer", "dean", "head_of_department")),
    proposal_repo=Depends(get_proposal_repo),
):
    proposal = await proposal_repo.create({
        "tenant_id": current_user.tenant_id or "default",
        "researcher_id": str(current_user.id),
        "status": "submitted",
        "submitted_date": datetime.utcnow(),
        **request.dict()
    })
    return {"id": str(proposal.id), "status": "submitted"}

@router.get("/proposals/pending")
async def list_pending_proposals(
    current_user: User = Depends(require_roles("head_of_department", "dean", "university_admin")),
    proposal_repo=Depends(get_proposal_repo),
):
    proposals = await proposal_repo.get_pending(current_user.tenant_id or "default")
    return [{"id": str(p.id), "title": p.title, "researcher_id": p.researcher_id} for p in proposals]

@router.post("/proposals/{proposal_id}/approve")
async def approve_proposal(
    proposal_id: str,
    current_user: User = Depends(require_roles("head_of_department", "dean", "university_admin")),
    proposal_repo=Depends(get_proposal_repo),
):
    await proposal_repo.update(proposal_id, {"status": "approved", "approved_date": datetime.utcnow()})
    return {"id": proposal_id, "status": "approved"}

@router.post("/grants")
async def create_grant(
    request: CreateGrantRequest,
    current_user: User = Depends(get_current_user),
    grant_repo=Depends(get_grant_repo),
):
    grant = await grant_repo.create({
        "tenant_id": current_user.tenant_id or "default",
        "researcher_id": str(current_user.id),
        **request.dict()
    })
    return {"id": str(grant.id)}

@router.post("/publications")
async def add_publication(
    request: CreatePublicationRequest,
    current_user: User = Depends(get_current_user),
    publication_repo=Depends(get_publication_repo),
):
    publication = await publication_repo.create({
        "tenant_id": current_user.tenant_id or "default",
        "researcher_id": str(current_user.id),
        **request.dict()
    })
    return {"id": str(publication.id)}

@router.get("/my-publications")
async def get_my_publications(
    current_user: User = Depends(get_current_user),
    publication_repo=Depends(get_publication_repo),
):
    publications = await publication_repo.get_by_researcher(str(current_user.id))
    return [{"id": str(p.id), "title": p.title, "journal": p.journal} for p in publications]
