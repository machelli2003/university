from typing import Iterable, List, Optional
import logging

from app.infrastructure.database.repositories.notification_repository import NotificationRepository
from app.infrastructure.database.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


async def create_notification_for_users(
    recipient_ids: Iterable[str],
    title: str,
    message: str,
    target_url: Optional[str] = None,
    tenant_id: str = "default",
    notification_type: str = "in_app",
):
    try:
        repo = NotificationRepository()
        seen = set()
        for recipient_id in recipient_ids:
            if not recipient_id or recipient_id in seen:
                continue
            seen.add(recipient_id)
            try:
                await repo.create({
                    "tenant_id": tenant_id,
                    "recipient_id": str(recipient_id),
                    "title": title,
                    "message": message,
                    "notification_type": notification_type,
                    "target_url": target_url,
                })
            except Exception as e:
                logger.error(f"Failed to create notification for {recipient_id}: {e}")
    except Exception as e:
        logger.error(f"Failed to create notifications: {e}")


async def notify_super_admins_for_application(
    tenant_id: Optional[str],
    title: str,
    message: str,
    target_url: Optional[str] = None,
):
    try:
        user_repo = UserRepository()
        users = await user_repo.model.find({"role": "super_admin"}).to_list(None)
        if users:
            await create_notification_for_users(
                [str(user.id) for user in users],
                title=title,
                message=message,
                target_url=target_url,
                tenant_id=tenant_id or "default",
            )
    except Exception as e:
        logger.error(f"Failed to notify super admins: {e}")


async def notify_application_admin(
    admin_email: Optional[str],
    title: str,
    message: str,
    target_url: Optional[str] = None,
    tenant_id: str = "default",
):
    if not admin_email:
        logger.debug("Skipping notification - no admin email provided")
        return
    try:
        user_repo = UserRepository()
        user = await user_repo.get_by_email(admin_email)
        if user:
            await create_notification_for_users(
                [str(user.id)],
                title=title,
                message=message,
                target_url=target_url,
                tenant_id=tenant_id,
            )
        else:
            logger.warning(f"Admin user not found for email: {admin_email}")
    except Exception as e:
        logger.error(f"Failed to notify admin {admin_email}: {e}")
