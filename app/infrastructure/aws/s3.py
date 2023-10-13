import logging
from io import BytesIO
from typing import Any

from boto3_type_annotations.s3 import Client
from botocore.exceptions import ClientError


class S3Service:
    s3_client: Client

    def __init__(self, s3_client: Client) -> None:
        self.logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}",
        )
        self.s3_client = s3_client

    def get_file_path(self, bucket_name: str, file_path: str) -> str:
        try:
            self.s3_client.head_object(Bucket=bucket_name, Key=file_path)
            return file_path
        except ClientError:
            return ""

    def upload_file(
            self, file: BytesIO, bucket_name: str, key: str
    ) -> None:
        self.s3_client.upload_fileobj(
            file,
            Bucket=bucket_name,
            Key=key,
        )

    def get_file(self, file_path: str, bucket_name: str) -> Any:
        obj = self.s3_client.get_object(Bucket=bucket_name, Key=file_path)
        obj = obj["Body"].read()
        return obj

    def create_pre_signed_url(
            self, bucket_name: str, object_name: str, expiration: int = 3600
    ) -> str:
        """Generate a preSigned URL to share an S3 object
        :param bucket_name: string
        :param object_name: string
        :param expiration: Time in seconds for the presigned URL to remain valid
        :return: Presigned URL as string. If error, returns None.
        """
        # Generate a preSigned URL for the S3 object
        response = self.s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": object_name},
            ExpiresIn=expiration,
        )
        # The response contains the preSigned URL
        return response

    def list_s3_objects_in_bucket(
            self,
            user_id: str,
            bucket_name: str
    ) -> dict:
        """
        This function will list down all files in a folder from S3 bucket
        :return: None
        """
        prefix = f"user/{user_id}"
        return self.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
