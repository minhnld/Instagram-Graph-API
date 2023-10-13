from typing import List, Optional

from pydantic import BaseModel
from pydantic.fields import Field


class GetInstagramBusinessAccountInfoInput(BaseModel):
    page_id: Optional[str]


class PostImageToInstagramBusinessAccountInput(BaseModel):
    instagram_business_account_id: str
    image_url: str
    caption: Optional[str]


class GetImagePostInsightsFromInstagramBusinessAccountInput(BaseModel):
    media_id: str


class GetAllMediasInfoFromInstagramBusinessAccountInput(BaseModel):
    instagram_business_account_id: str


class Permission(BaseModel):
    permission: str
    status: str


class Permissions(BaseModel):
    data: Optional[List[Permission]]


class Me(BaseModel):
    id: str
    name: str
    permissions: Permissions
    token: Optional[str] = Field(None)
