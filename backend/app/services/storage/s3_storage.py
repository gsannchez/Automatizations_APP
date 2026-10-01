import logging
import boto3
from botocore.exceptions import ClientError
from typing import Optional
from .storage_provider import StorageProvider

logger = logging.getLogger(__name__)

class S3StorageProvider(StorageProvider):
    """S3-compatible storage implementation."""
    
    def __init__(self, bucket_name: str, endpoint_url: Optional[str] = None):
        self.bucket_name = bucket_name
        self.s3_client = boto3.client('s3', endpoint_url=endpoint_url)

    async def upload_file(self, source_path: str, destination_key: str) -> str:
        try:
            # Note: For strict async, use aioboto3. Using sync boto3 here for simplicity in wrapper.
            self.s3_client.upload_file(source_path, self.bucket_name, destination_key)
            logger.debug(f"[S3Storage] Uploaded {source_path} to s3://{self.bucket_name}/{destination_key}")
            return f"s3://{self.bucket_name}/{destination_key}"
        except ClientError as e:
            logger.error(f"[S3Storage] Upload failed: {e}")
            raise

    async def download_file(self, source_key: str, destination_path: str) -> bool:
        try:
            self.s3_client.download_file(self.bucket_name, source_key, destination_path)
            return True
        except ClientError as e:
            logger.error(f"[S3Storage] Download failed: {e}")
            return False

    async def get_signed_url(self, key: str, expires_in: int = 3600) -> str:
        try:
            url = self.s3_client.generate_presigned_url('get_object',
                                                        Params={'Bucket': self.bucket_name,
                                                                'Key': key},
                                                        ExpiresIn=expires_in)
            return url
        except ClientError as e:
            logger.error(f"[S3Storage] Signed URL generation failed: {e}")
            raise

    async def delete_file(self, key: str) -> bool:
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError as e:
            logger.error(f"[S3Storage] Delete failed: {e}")
            return False
