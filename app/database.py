from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base

DB_PATH = Path(__file__).resolve().parent.parent / "nexo.db"

_engine = None
SessionLocal = None


def init_db(url: str | None = None):
    """(Re)configura o engine e a fábrica de sessões."""
    global _engine, SessionLocal
    if url is None:
        url = f"sqlite:///{DB_PATH}"

    _engine = create_engine(url, echo=False)
    Base.metadata.create_all(_engine)
    SessionLocal = sessionmaker(
        bind=_engine, autoflush=False, expire_on_commit=False
    )
    return _engine


def get_engine():
    if _engine is None:
        init_db()
    return _engine


init_db()
