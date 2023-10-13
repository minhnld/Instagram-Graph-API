import logging
from contextlib import AbstractContextManager
from typing import Callable
from psycopg2 import errors

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.db.image_publishing_metadata import InstagramImagePublishingMetadata

UniqueViolation = errors.lookup("23505")  # Correct way to Import the psycopg2 errors


class CreateWithCategoryResponse:
    pass


class InstagramImageUploadMetadataRepository:
    def __init__(
            self,
            session_factory: Callable[..., AbstractContextManager[Session]]
    ) -> None:
        self.session_factory = session_factory
        self.logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}",
        )

    def add(self, image_publish_metadata: InstagramImagePublishingMetadata) -> InstagramImagePublishingMetadata | None:
        with self.session_factory() as session:
            try:
                session.add(image_publish_metadata)
                session.commit()
                session.refresh(image_publish_metadata)
                return image_publish_metadata
            except IntegrityError as err:
                self.logger.error(err)
                if isinstance(err.orig, UniqueViolation):
                    raise NotUniqueError(err.orig.pgcode, err.orig.pgerror)
            except SQLAlchemyError as err:
                self.logger.error(err)
            return None


class NotUniqueError(Exception):
    def __init__(self, pg_code: str, pg_error: str):
        super().__init__(f" DB error_code: {pg_code} DB error_msg: {pg_error}")
