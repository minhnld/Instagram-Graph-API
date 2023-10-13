from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    func,
)

from app.infrastructure.db.database import Base


class InstagramImagePublishingMetadata(Base):
    __tablename__ = "instagram_image_publishing_metadata"
    id = Column(Integer, primary_key=True)
    instagram_business_account_id = Column(String, nullable=False, unique=True)
    auth_id = Column(String, nullable=False, unique=True)
    image_url = Column(String)
    caption = Column(String, nullable=True)
    instagram_media_container_id = Column(String, nullable=False, unique=True)
    instagram_media_published_id = Column(String, nullable=False, unique=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())