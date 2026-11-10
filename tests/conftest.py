import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import database
from app.models import Base


@pytest.fixture
def db_session(tmp_path, monkeypatch):
    """Banco SQLite isolado por teste."""
    url = f"sqlite:///{tmp_path}/test.db"
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(
        bind=engine, autoflush=False, expire_on_commit=False
    )
    monkeypatch.setattr(database, "SessionLocal", TestSession)
    yield TestSession
    engine.dispose()
