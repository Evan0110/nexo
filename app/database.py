from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base

# Banco fica na raiz do projeto: ~/Documents/nexo/nexo.db
DB_PATH = Path(__file__).resolve().parent.parent / "nexo.db"

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

# Cria as tabelas se ainda não existirem
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
