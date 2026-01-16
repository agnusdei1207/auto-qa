import os
import logging
from datetime import datetime
from typing import Optional

try:
    from minio import Minio
    from minio.error import S3Error
    MINIO_AVAILABLE = True
except ImportError:
    MINIO_AVAILABLE = False
    S3Error = Exception

logger = logging.getLogger(__name__)


class MinioClient:
    def __init__(self):
        if not MINIO_AVAILABLE:
            logger.error("minio package not installed. Install with: pip install minio")
            raise ImportError("minio package required but not installed")

        self.endpoint = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
        self.access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
        self.secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
        self.bucket_name = os.getenv("MINIO_BUCKET", "qa-screenshots")
        self.secure = os.getenv("MINIO_SECURE", "false").lower() == "true"

        self.client = Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure
        )

        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created MinIO bucket: {self.bucket_name}")
            else:
                logger.info(f"MinIO bucket exists: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Failed to ensure bucket exists: {e}")
            raise

    def upload_screenshot(
        self,
        session_id: str,
        image_bytes: bytes,
        full_page: bool = False
    ) -> Optional[str]:
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            object_name = f"screenshots/{session_id}/screenshot_{timestamp}.png"

            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=io.BytesIO(image_bytes),
                length=len(image_bytes),
                content_type="image/png"
            )

            public_url = self._get_public_url(object_name)
            logger.info(f"Screenshot uploaded to MinIO: {public_url}")
            return public_url

        except S3Error as e:
            logger.error(f"Failed to upload screenshot to MinIO: {e}")
            return None

    def _get_public_url(self, object_name: str) -> str:
        if self.secure:
            protocol = "https"
        else:
            protocol = "http"

        return f"{protocol}://{self.endpoint.replace('http://', '').replace('https://', '')}/{self.bucket_name}/{object_name}"

    def health_check(self) -> bool:
        try:
            self.client.list_buckets()
            return True
        except S3Error:
            return False


import io
