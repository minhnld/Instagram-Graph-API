import logging

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.container.containers import Container
from app.models.schemas.instagram import Me
from app.services.instagram_account_management import InstagramAccountManageService

logger = logging.getLogger()
router = APIRouter()


@router.post("/facebook")
@inject
def check_user_facebook(
        token: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        account_management_service: InstagramAccountManageService = Depends(Provide[Container.account_management_service]),
) -> Me:
    return account_management_service.verify_token(token.credentials)
