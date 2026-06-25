from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import get_settings

settings = get_settings()

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


_DEFAULT_HOSTS = [
    {"name": "Google DNS", "ip_address": "8.8.8.8", "is_default": True},
    {"name": "Cloudflare DNS", "ip_address": "1.1.1.1", "is_default": True},
]


def _seed_default_hosts() -> None:
    from app.models import Host

    db = SessionLocal()
    try:
        if db.query(Host).first() is None:
            db.add_all(Host(**data) for data in _DEFAULT_HOSTS)
            db.commit()
    finally:
        db.close()


def init_db() -> None:
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _seed_default_hosts()
