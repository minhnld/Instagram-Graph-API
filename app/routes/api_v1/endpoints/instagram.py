from http import HTTPStatus

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.container.containers import Container
from app.infrastructure.meta.instagram_platform.graph_api import InstagramGraphApiClient

from app.models.schemas.instagram import GetInstagramBusinessAccountInfoInput, Me, \
    PostImageToInstagramBusinessAccountInput
from app.routes.api_v1.endpoints.auth import check_user_facebook

ERROR_UPLOADING_FILES = "We have an error uploading files"

router = APIRouter()


@router.get("/account")
@inject
async def get_instagram_business_account_info(
        auth: Me = Depends(check_user_facebook),
        input_params: GetInstagramBusinessAccountInfoInput = Depends(),
        instagram_graph_api_client: InstagramGraphApiClient = Depends(Provide[Container.instagram_graph_api_client]),
):
    result = instagram_graph_api_client.get_instagram_account(
        auth.token,
        page_id=input_params.page_id
    )
    if result:
        return result
    raise HTTPException(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        detail=ERROR_UPLOADING_FILES,
    )


@router.get("/user_pages")
@inject
async def get_user_pages(
        auth: Me = Depends(check_user_facebook),
        instagram_graph_api_client: InstagramGraphApiClient = Depends(Provide[Container.instagram_graph_api_client]),
):
    result = instagram_graph_api_client.get_user_pages(
        auth.token
    )
    if result:
        return result
    raise HTTPException(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        detail=ERROR_UPLOADING_FILES,
    )


@router.post("/image")
@inject
async def publish_image(
        input_params: PostImageToInstagramBusinessAccountInput,
        auth: Me = Depends(check_user_facebook),
        instagram_graph_api_client: InstagramGraphApiClient = Depends(Provide[Container.instagram_graph_api_client]),
):
    image_container = instagram_graph_api_client.create_image_container(
        auth.token,
        input_params.instagram_business_account_id,
        input_params.image_url,
        input_params.caption
    )

    result = instagram_graph_api_client.publish_image(
        auth.token,
        input_params.instagram_business_account_id,
        image_container['json_data']['id']
    )

    if result:
        return result
    raise HTTPException(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        detail=ERROR_UPLOADING_FILES,
    )
