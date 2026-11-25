from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


def make_session_factory(database_url: str) -> sessionmaker:
    kwargs = {}
    if database_url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
        if database_url in ("sqlite://", "sqlite:///:memory:"):
            # One shared connection so an in-memory database survives across sessions.
            kwargs["poolclass"] = StaticPool
    engine = create_engine(database_url, **kwargs)

    from . import models  # noqa: F401  (registers the tables)

    Base.metadata.create_all(engine)
    return sessionmaker(engine, expire_on_commit=False)
