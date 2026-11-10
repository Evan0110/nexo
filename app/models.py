from datetime import date

from sqlalchemy import String, Integer, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Membro(Base):
    __tablename__ = "membros"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    matricula: Mapped[str | None] = mapped_column(String(30), unique=True, nullable=True)
    cargo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    departamento: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    telefone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    data_ingresso: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="Ativo")

    def __repr__(self) -> str:
        return f"Membro(id={self.id!r}, nome={self.nome!r}, matricula={self.matricula!r})"
