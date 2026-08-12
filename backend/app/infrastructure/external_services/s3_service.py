from typing import Optional
import logging
import aiobotocore.session

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class S3Service:
    """
    File storage service supporting stub or AWS S3.
    """

    def __init__(self):
        self.provider = settings.FILE_STORAGE_PROVIDER.lower() if settings.FILE_STORAGE_PROVIDER else "stub"
        self.enabled = self.provider == "s3"

    async def upload_file(
        self,
        file_content: bytes,
        file_name: str,
        content_type: str = "application/octet-stream",
    ) -> dict:
        if self.provider == "s3":
            return await self._upload_s3(file_content, file_name, content_type)

        mock_url = f"https://storage.stub.local/uploads/{file_name}"
        logger.info(f"[S3 STUB] Would upload: {file_name}")
        return {
            "uploaded": False,
            "stub": True,
            "url": mock_url,
            "message": "S3 not configured. Mock URL returned.",
        }

    async def _upload_s3(
        self,
        file_content: bytes,
        file_name: str,
        content_type: str = "application/octet-stream",
    ) -> dict:
        if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY or not settings.AWS_S3_BUCKET or not settings.AWS_S3_REGION:
            logger.error("S3 provider selected but AWS credentials or bucket info is not configured")
            return {"uploaded": False, "message": "AWS S3 not configured."}

        session = aiobotocore.session.get_session()
        endpoint_url = settings.AWS_S3_ENDPOINT_URL

        async with session.create_client(
            "s3",
            region_name=settings.AWS_S3_REGION,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            endpoint_url=endpoint_url,
        ) as client:
            try:
                await client.put_object(
                    Bucket=settings.AWS_S3_BUCKET,
                    Key=file_name,
                    Body=file_content,
                    ContentType=content_type,
                )

                url = f"https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_S3_REGION}.amazonaws.com/{file_name}"
                return {"uploaded": True, "url": url}
            except Exception as exc:
                logger.error(f"S3 upload failed: {exc}")
                return {"uploaded": False, "message": str(exc)}

    async def delete_file(self, file_url: str) -> bool:
        if self.provider != "s3":
            logger.info(f"[S3 STUB] Would delete: {file_url}")
            return True

        object_key = file_url.split("/")[-1]
        session = aiobotocore.session.get_session()

        async with session.create_client(
            "s3",
            region_name=settings.AWS_S3_REGION,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        ) as client:
            try:
                await client.delete_object(Bucket=settings.AWS_S3_BUCKET, Key=object_key)
                return True
            except Exception as exc:
                logger.error(f"S3 delete failed: {exc}")
                return False
