import io
import pathlib
from http import HTTPStatus
from typing import Dict, List

from PIL import Image, UnidentifiedImageError
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from app.container.containers import Container
from app.infrastructure.aws.s3 import (
    S3FilesInFolderResponse,
    S3Service,
    UploadS3FileResponse,
)
from app.models.schemas.instagram import Me
from app.routes.api_v1.endpoints.auth import check_user_facebook

#
router = APIRouter()


@router.post("")
@inject
async def upload_image_to_s3(
    image_file: UploadFile,
    s3_image_bucket: str = Depends(Provide[Container.s3_image_bucket]),
    auth: Me = Depends(check_user_facebook),
    s3_service: S3Service = Depends(Provide[Container.s3_service]),
) -> UploadS3FileResponse:
    file_extension = pathlib.Path(image_file.filename).suffix
    if file_extension not in [".png", ".jpg", ".jpeg"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="the file you uploaded was not a valid image",
        )
    image_file.file.seek(0)
    contents = image_file.file.read()
    temp_file = io.BytesIO()
    temp_file.write(contents)
    temp_file.seek(0)

    try:
        Image.open(temp_file)
    except UnidentifiedImageError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Your image is corrupted or damaged",
        )
    result = s3_service.upload_file(
        file=temp_file,
        bucket_name=s3_image_bucket,
        user_id=auth.id,
        extension=file_extension,
    )
    if result:
        return result
    raise HTTPException(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        detail="We have an error uploading files",
    )


@router.get("")
@inject
async def get_user_uploaded_images(
    auth: Me = Depends(check_user_facebook),
    s3_service: S3Service = Depends(Provide[Container.s3_service]),
    s3_image_bucket: str = Depends(Provide[Container.s3_image_bucket]),
) -> Dict[str, List[S3FilesInFolderResponse]]:
    return {
        "items": s3_service.list_s3_files_in_folder(
            bucket_name=s3_image_bucket,
            user_id=auth.id,
        )
    }
