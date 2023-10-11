import logging
from contextlib import AbstractContextManager
from typing import Any, Callable, Dict, Generic, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import UnaryExpression

from app.infrastructure.db.database import Base
from app.models.common.pagination import PagedResponseSchema, paginate

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(
        self,
        model: Type[ModelType],
        session_factory: Callable[..., AbstractContextManager[Session]],
    ):
        self.model = model
        self.session_factory = session_factory
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def get(self, id: Any) -> PagedResponseSchema[ModelType]:
        with self.session_factory() as session:
            query = session.query(self.model).filter(self.model.id == id)
            return PagedResponseSchema(
                total=query.count(),
                total_page=1,
                items=[query.first()],
            )

    def query(
        self,
        query: Any,
        page: int,
        size: int,
        sort_by: Optional[UnaryExpression[Any]] = None,
    ) -> PagedResponseSchema[ModelType]:
        with self.session_factory() as session:
            if sort_by is not None:
                query = session.query(self.model).filter(query).order_by(sort_by)
            else:
                query = session.query(self.model).filter(query)
            return paginate(page, size, query)

    def get_multi(
        self, page: int, size: int, sort_by: Optional[UnaryExpression[Any]] = None
    ) -> PagedResponseSchema[ModelType]:
        with self.session_factory() as session:
            if sort_by is not None:
                query = session.query(self.model).order_by(sort_by)
            else:
                query = session.query(self.model)
            return paginate(page, size, query)

    def create(
        self, *, obj_in: CreateSchemaType, commit: bool = True
    ) -> Optional[ModelType]:
        with self.session_factory() as session:
            obj_in_data = jsonable_encoder(obj_in)
            db_obj = self.model(**obj_in_data)
            session.add(db_obj)
            if commit:
                session.commit()
                session.refresh(db_obj)
            return db_obj

    def update(
        self,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
        commit: bool = True,
    ) -> Optional[ModelType]:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        with self.session_factory() as session:
            session.add(db_obj)
            if commit:
                session.commit()
                session.refresh(db_obj)
            return db_obj

    def remove(self, *, id: int, commit: bool = True) -> Optional[ModelType]:
        with self.session_factory() as session:
            obj = session.query(self.model).get(id)
            session.delete(obj)
            if commit:
                session.commit()
            return obj
