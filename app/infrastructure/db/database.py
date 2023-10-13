import logging
from contextlib import AbstractContextManager, contextmanager
from typing import Callable

from sqlalchemy import create_engine, create_mock_engine, orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base()


def dump(sql, *multiparams, **params):  # type: ignore
    print()


class Database:

    def __init__(self, db_url: str) -> None:
        self.logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}",
        )

        self._engine = (
            create_engine(db_url, echo=True)
            if db_url
            else create_mock_engine("postgresql+psycopg2://", dump)
        )

        self._session_factory = orm.scoped_session(
            orm.sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
            ),
        )

    def create_database(self) -> None:
        Base.metadata.create_all(self._engine)

    @contextmanager  # type: ignore
    def session(self) -> Callable[..., AbstractContextManager[Session]]:  # type: ignore
        session: Session = self._session_factory()
        try:
            yield session
        except Exception:
            self.logger.exception("Session rollback because of exception")
            session.rollback()
            raise
        finally:
            session.close()
