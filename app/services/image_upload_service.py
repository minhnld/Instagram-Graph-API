import json
from json import JSONDecodeError
from typing import Any, Generator

from app.infrastructure.meta.instagram_platform.graph_api import InstagramGraphApiClient
from app.models.common.pagination import PagedResponseSchema
from app.models.schemas.instagram import PostImageToInstagramBusinessAccountInput

from app.repositories.image_upload_history_repository import ImageUploadHistoryRepository
from app.services.base_service import BaseService


class MediaUploadService(BaseService):
    def __init__(
            self,
            instagram_graph_api_client: InstagramGraphApiClient,
            image_upload_history_repository: ImageUploadHistoryRepository,
            s3: ImageUploadHistoryRepository,
    ):
        super().__init__(image_upload_history_repository)

        self.instagram_graph_api_client = instagram_graph_api_client
        self.s3 = s3

    def post_image_to_instagram(
            self,
            input_params: PostImageToInstagramBusinessAccountInput,
            token: str,
    ):
        image_container = self.instagram_graph_api_client.create_image_container(
            token,
            input_params.instagram_business_account_id,
            input_params.image_url,
            input_params.caption
        )
        result = self.instagram_graph_api_client.publish_image(
            token,
            input_params.instagram_business_account_id,
            image_container['json_data']['id']
        )
        return result






class PromptParserException(Exception):
    def __init__(self) -> None:
        super().__init__("Can not parse prompt response to json")
