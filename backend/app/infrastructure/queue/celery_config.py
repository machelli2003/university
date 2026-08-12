from celery import Celery
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "eump",
    broker=settings.CELERY_BROKER,
    backend=settings.CELERY_BACKEND,
    include=["app.infrastructure.queue.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Africa/Accra",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
)
