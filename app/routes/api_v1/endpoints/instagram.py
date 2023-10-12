from http import HTTPStatus

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException

from app.container.containers import Container
from app.models.schemas.instagram import GetInstagramBusinessAccountInfoInput, Me, \
    PostImageToInstagramBusinessAccountInput, GetImagePostInsightsFromInstagramBusinessAccountInput, \
    GetAllMediasInfoFromInstagramBusinessAccountInput
from app.routes.api_v1.endpoints.auth import check_user_facebook
from app.services.instagram_account_management import InstagramAccountManageService
from app.services.instagram_media_insights import MediaInsightService
from app.services.instagram_media_upload_service import MediaUploadService

ERROR_UPLOADING_FILES = "We have an error uploading files"

router = APIRouter()


@router.get("/account")
@inject
async def get_instagram_business_account_info(
        auth: Me = Depends(check_user_facebook),
        input_params: GetInstagramBusinessAccountInfoInput = Depends(),
        account_management_service: InstagramAccountManageService = Depends(Provide[Container.account_management_service]),
):
    result = account_management_service.get_instagram_account_info(input_params.page_id, auth.token)
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
        account_management_service: InstagramAccountManageService = Depends(Provide[Container.account_management_service]),
):
    result = account_management_service.get_user_pages(
        auth.token
    )
    if result:
        return result
    raise HTTPException(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        detail=ERROR_UPLOADING_FILES,
    )


@router.post("/images")
@inject
async def publish_image(
        input_params: PostImageToInstagramBusinessAccountInput,
        auth: Me = Depends(check_user_facebook),
        media_upload_service: MediaUploadService = Depends(Provide[Container.media_upload_service]),
):
    result = media_upload_service.post_image_to_instagram(input_params, auth.token, auth.id)
    if result:
        return result
    raise HTTPException(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        detail=ERROR_UPLOADING_FILES,
    )


@router.get("/images/{media_id}/insights")
@inject
async def get_image_insights(
        input_params: GetImagePostInsightsFromInstagramBusinessAccountInput = Depends(),
        auth: Me = Depends(check_user_facebook),
        media_insight_service: MediaInsightService = Depends(Provide[Container.media_insight_service]),
):
    result = media_insight_service.get_image_insights(input_params, auth.token)
    if result:
        return result
    raise HTTPException(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        detail=ERROR_UPLOADING_FILES,
    )


@router.get("/medias")
@inject
async def list_all_medias(
        input_params: GetAllMediasInfoFromInstagramBusinessAccountInput = Depends(),
        auth: Me = Depends(check_user_facebook),
        media_insight_service: MediaInsightService = Depends(Provide[Container.media_insight_service]),
):
    result = media_insight_service.get_list_all_instagram_medias(input_params, auth.token)
    if result:
        return result
    raise HTTPException(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        detail=ERROR_UPLOADING_FILES,
    )
