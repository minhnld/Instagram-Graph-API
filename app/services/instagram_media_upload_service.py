from typing import List

from app.infrastructure.aws.s3 import S3Service
from app.infrastructure.meta.instagram_platform.graph_api import InstagramGraphApiClient
from app.models.db.image_publishing_metadata import InstagramImagePublishingMetadata
from app.models.schemas.aws_s3 import UploadS3FileResponse, S3FilesInFolderResponse
from app.models.schemas.instagram import PostImageToInstagramBusinessAccountInput
from io import BytesIO
import hashlib

from app.repositories.instagram_image_upload_history_repository import InstagramImageUploadMetadataRepository


class MediaUploadService:
    def __init__(
            self,
            instagram_graph_api_client: InstagramGraphApiClient,
            image_upload_metadata_repository: InstagramImageUploadMetadataRepository,
            s3: S3Service,
    ):
        self.instagram_graph_api_client = instagram_graph_api_client
        self.image_upload_metadata_repository = image_upload_metadata_repository
        self.s3 = s3

    def post_image_to_instagram(
            self,
            input_params: PostImageToInstagramBusinessAccountInput,
            token: str,
            auth_id: str,
    ):
        image_container = self.instagram_graph_api_client.create_image_container(
            token,
            input_params.instagram_business_account_id,
            input_params.image_url,
            input_params.caption
        )
        instagram_media_container_id = image_container['json_data']['id']
        result = self.instagram_graph_api_client.publish_image(
            token,
            input_params.instagram_business_account_id,
            instagram_media_container_id
        )
        instagram_media_published_id = result['json_data']['id']
        self.image_upload_metadata_repository.add(
            InstagramImagePublishingMetadata(
                instagram_business_account_id=input_params.instagram_business_account_id,
                auth_id=auth_id,
                image_url=input_params.image_url,
                caption=input_params.caption,
                instagram_media_container_id=instagram_media_container_id,
                instagram_media_published_id=instagram_media_published_id,
            )
        )
        return result

    def upload_file_to_s3(
            self,
            file: BytesIO,
            user_id: str,
            bucket_name: str,
            extension: str
    ) -> UploadS3FileResponse | None:
        hashed_name = hashlib.sha256(file.read()).hexdigest()
        upload_path = f"user/{user_id}/{hashed_name}{extension}"
        path = self.s3.get_file_path(bucket_name, upload_path)
        if path:
            return UploadS3FileResponse(
                upload_path,
                self.s3.create_pre_signed_url(bucket_name, upload_path)
            )
        file.seek(0)
        self.s3.upload_file(
            file,
            bucket_name=bucket_name,
            key=upload_path,
        )
        self.logger.debug(
            "File %s has been successfully uploaded by user %s",
            upload_path,
            user_id,
        )

        return UploadS3FileResponse(
            upload_path, self.s3.create_pre_signed_url(bucket_name, upload_path)
        )

    def list_s3_files_in_folder(
            self,
            bucket_name: str,
            user_id: str
    ) -> List[S3FilesInFolderResponse]:
        get_s3_objects_payload = self.s3.list_s3_objects_in_bucket(
            user_id,
            bucket_name
        )
        files = get_s3_objects_payload.get("Contents")
        return (
            [
                S3FilesInFolderResponse(
                    file["Key"],
                    self.s3.create_pre_signed_url(bucket_name, file["Key"]),
                    str(file["LastModified"]),
                )
                for file in files
            ]
            if files
            else []
        )


class PromptParserException(Exception):
    def __init__(self) -> None:
        super().__init__("Can not parse prompt response to json")
