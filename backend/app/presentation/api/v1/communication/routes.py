from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.presentation.api.v1.communication.schemas import (
    SendNotificationRequest, CreateCampaignRequest
)
from app.infrastructure.database.repositories.notification_repository import (
    NotificationRepository, CampaignRepository
)
from app.dependencies import get_current_user, require_roles
from app.infrastructure.models.user import User

router = APIRouter()

def get_notification_repo() -> NotificationRepository:
    return NotificationRepository()

def get_campaign_repo() -> CampaignRepository:
    return CampaignRepository()

@router.post("/notifications/send")
async def send_notification(
    request: SendNotificationRequest,
    current_user: User = Depends(require_roles("university_admin", "super_admin", "registrar")),
    notification_repo=Depends(get_notification_repo),
):
    notification = await notification_repo.create({
        "tenant_id": current_user.tenant_id or "default",
        **request.dict()
    })
    return {"id": str(notification.id)}

@router.get("/notifications/my")
async def get_my_notifications(
    current_user: User = Depends(get_current_user),
    notification_repo=Depends(get_notification_repo),
):
    notifications = await notification_repo.get_by_recipient(str(current_user.id))
    return [
        {"id": str(n.id), "title": n.title, "message": n.message, "is_read": n.is_read}
        for n in notifications
    ]

@router.post("/notifications/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    notification_repo=Depends(get_notification_repo),
):
    await notification_repo.mark_as_read(notification_id)
    return {"status": "read"}

@router.post("/campaigns")
async def create_campaign(
    request: CreateCampaignRequest,
    current_user: User = Depends(require_roles("university_admin", "super_admin")),
    campaign_repo=Depends(get_campaign_repo),
):
    campaign = await campaign_repo.create({
        "tenant_id": current_user.tenant_id or "default",
        "created_by": str(current_user.id),
        **request.dict()
    })
    return {"id": str(campaign.id)}

@router.get("/campaigns")
async def list_campaigns(
    current_user: User = Depends(require_roles("university_admin", "super_admin")),
    campaign_repo=Depends(get_campaign_repo),
):
    campaigns = await campaign_repo.get_by_tenant(current_user.tenant_id or "default")
    return [{"id": str(c.id), "name": c.name, "message": c.message} for c in campaigns]
