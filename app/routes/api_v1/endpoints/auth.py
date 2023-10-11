import logging

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.container.containers import Container
from app.infrastructure.meta.instagram_platform.graph_api import InstagramGraphApiClient
from app.models.schemas.instagram import Me

logger = logging.getLogger()
router = APIRouter()


@router.post("/facebook")
@inject
def check_user_facebook(
        token: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        instagram_graph_api_client: InstagramGraphApiClient = Depends(Provide[Container.instagram_graph_api_client]),
) -> Me:
    return instagram_graph_api_client.me(token.credentials)
