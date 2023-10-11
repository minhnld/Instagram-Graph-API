from typing import Any
from unittest import mock

from app.infrastructure.auth0.auth0 import Auth0Service
from app.models.schemas.users import Auth0User


def get_http_header(bearer_key: str = "xyz") -> dict[str, Any]:
    return {
        "Accept": "application/json",
        "Authorization": f"Bearer {bearer_key}",
    }


def mock_user() -> mock.Mock:
    auth_service_mock = mock.Mock(spec=Auth0Service)
    auth_service_mock.verify_token.return_value = Auth0User(
        sub="user123", permissions=["read", "write"]
    )
    return auth_service_mock
