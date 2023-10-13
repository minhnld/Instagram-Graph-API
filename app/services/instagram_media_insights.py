from app.infrastructure.meta.instagram_platform.graph_api import InstagramGraphApiClient
from app.models.schemas.instagram import GetImagePostInsightsFromInstagramBusinessAccountInput, \
    GetAllMediasInfoFromInstagramBusinessAccountInput


class MediaInsightService:
    def __init__(
            self,
            instagram_graph_api_client: InstagramGraphApiClient,
    ):
        self.instagram_graph_api_client = instagram_graph_api_client

    def get_image_insights(
            self,
            input_params: GetImagePostInsightsFromInstagramBusinessAccountInput,
            token: str,
    ):
        return self.instagram_graph_api_client.get_image_insights(token, input_params.media_id)

    def get_list_all_instagram_medias(
            self,
            input_params: GetAllMediasInfoFromInstagramBusinessAccountInput,
            token: str,
    ):
        return self.instagram_graph_api_client.get_all_medias(token, input_params.instagram_business_account_id)
