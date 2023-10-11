from fastapi import APIRouter

from app.routes.api_v1.endpoints import (
    auth,
    image,
    instagram,
)

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(image.router, prefix="/image", tags=["image"])
router.include_router(instagram.router, prefix="/instagram", tags=["instagram"])
