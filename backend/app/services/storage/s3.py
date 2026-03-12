import os
import boto3
from typing import BinaryIO, Union
from botocore.exceptions import ClientError
from .base import BaseStorage

class S3Storage(BaseStorage):
    def __init__(self):
        self.bucket = os.getenv("S3_BUCKET_NAME")
        self.region = os.getenv("S3_REGION", "us-east-1")
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            endpoint_url=os.getenv("S3_ENDPOINT_URL"), # Para MinIO
            region_name=self.region
        )

    def save(self, file_obj: Union[BinaryIO, bytes], path: str) -> str:
        try:
            if isinstance(file_obj, bytes):
                self.s3_client.put_object(Bucket=self.bucket, Key=path, Body=file_obj)
            else:
                self.s3_client.upload_fileobj(file_obj, self.bucket, path)
            return path
        except ClientError as e:
            print(f"Error uploading to S3: {e}")
            raise e

    def get_url(self, path: str) -> str:
        # Generar URL firmada (presigned url) por defecto para seguridad
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': path},
                ExpiresIn=3600
            )
            return url
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return ""

    def get_local_path(self, path: str) -> str:
        # Para FFmpeg necesitamos el archivo local. Lo descargamos a /tmp
        tmp_path = f"/tmp/{os.path.basename(path)}" # Ojo en Windows, usar tempfile
        try:
            self.s3_client.download_file(self.bucket, path, tmp_path)
            return tmp_path
        except ClientError as e:
            print(f"Error downloading from S3: {e}")
            raise e

    def delete(self, path: str) -> bool:
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=path)
            return True
        except ClientError as e:
            print(f"Error deleting from S3: {e}")
            return False
