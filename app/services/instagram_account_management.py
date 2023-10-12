from typing import Optional

from app.infrastructure.meta.instagram_platform.graph_api import InstagramGraphApiClient


class InstagramAccountManageService:
    def __init__(
            self,
            instagram_graph_api_client: InstagramGraphApiClient,
    ):
        self.instagram_graph_api_client = instagram_graph_api_client

    def get_instagram_account_info(
            self,
            page_id: Optional[str],
            token: str,
    ):
        if page_id:
            result = self.instagram_graph_api_client.get_instagram_account(
                token,
                page_id=page_id
            )
        else:
            result = self.instagram_graph_api_client.get_instagram_accounts(
                token,
            )
        return result

    def get_user_pages(
            self,
            token: str,
    ):
        return self.instagram_graph_api_client.get_user_pages(token)
