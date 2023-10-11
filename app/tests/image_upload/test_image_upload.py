import os
from unittest import mock

import pytest
from fastapi.testclient import TestClient

from app.infrastructure.auth0.auth0 import Auth0Service
from app.infrastructure.aws.s3 import (
    S3FilesInFolderResponse,
    S3Service,
    UploadS3FileResponse,
)
from app.main import app
from app.models.schemas.users import Auth0User

APPLICATION_JSON = "application/json"


@pytest.fixture()
def client():
    return TestClient(app)


def test_upload_image(client):
    s3_service_mock = mock.Mock(spec=S3Service)
    s3_service_mock.upload_file.return_value = UploadS3FileResponse(
        "s3/bucket/path/key", "http://s3.image.jng"
    )

    auth_service_mock = mock.Mock(spec=Auth0Service)
    auth_service_mock.verify_token.return_value = Auth0User(
        sub="user123", permissions=["read", "write"]
    )

    app.container.s3_service.override(s3_service_mock)
    app.container.auth.override(auth_service_mock)

    image_path = os.path.join(os.path.dirname(__file__), "test_image.jpg")
    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()
        image_file = ("test_image.png", image_bytes, "image/png")
        response = client.post(
            "/api/v1/image",
            files={"image_file": image_file},
            headers={
                "Accept": APPLICATION_JSON,
                "Authorization": "Bearer xyz",
            },
        )

    assert response.status_code == 200
    assert response.json() == {
        "full_url": "http://s3.image.jng",
        "s3_bucket_path_key": "s3/bucket/path/key",
    }
    s3_service_mock.upload_file.assert_called_once_with(
        file=mock.ANY,
        bucket_name=mock.ANY,
        user_id="user123",  # Set the user_id based on the mock
        extension=".png",
    )


def test_get_images(client):
    auth_service_mock = mock.Mock(spec=Auth0Service)
    auth_service_mock.verify_token.return_value = Auth0User(
        sub="user123", permissions=["read", "write"]
    )
    s3_service_mock = mock.Mock(spec=S3Service)
    s3_service_mock.list_s3_files_in_folder.return_value = [
        S3FilesInFolderResponse(
            "s3/bucket/path/key1", "http://s31.image.jng", "23/3/2023"
        ),
        S3FilesInFolderResponse(
            "s3/bucket/path/key2", "http://s32.image.jng", "24/3/2023"
        ),
    ]
    app.container.auth.override(auth_service_mock)
    app.container.s3_service.override(s3_service_mock)

    response = client.get(
        "/api/v1/image",
        headers={
            "Accept": APPLICATION_JSON,
            "Authorization": "Bearer xyz",
        },
    )

    assert response.status_code == 200
    assert response.json()["items"] == [
        {
            "full_url": "http://s31.image.jng",
            "s3_bucket_path_key": "s3/bucket/path/key1",
            "last_modified": "23/3/2023",
        },
        {
            "full_url": "http://s32.image.jng",
            "s3_bucket_path_key": "s3/bucket/path/key2",
            "last_modified": "24/3/2023",
        },
    ]

    s3_service_mock.list_s3_files_in_folder.assert_called_once_with(
        bucket_name=mock.ANY,
        user_id="user123",  # Set the user_id based on the mock
    )
