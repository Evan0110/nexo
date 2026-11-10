from datetime import date

from sqlalchemy import String, Integer, Date, ForeignKey, UniqueConstraint
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


class Reuniao(Base):
    __tablename__ = "reunioes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    titulo: Mapped[str] = mapped_column(String(100), nullable=False)
    data: Mapped[date] = mapped_column(Date, nullable=False)
    tipo: Mapped[str] = mapped_column(String(30), default="Geral")

    def __repr__(self) -> str:
        return f"Reuniao(id={self.id!r}, titulo={self.titulo!r}, data={self.data!r})"


class Presenca(Base):
    __tablename__ = "presencas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reuniao_id: Mapped[int] = mapped_column(
        ForeignKey("reunioes.id"), nullable=False
    )
    membro_id: Mapped[int] = mapped_column(
        ForeignKey("membros.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), default="Presente")

    __table_args__ = (
        UniqueConstraint("reuniao_id", "membro_id", name="uq_reuniao_membro"),
    )

    def __repr__(self) -> str:
        return f"Presenca(reuniao_id={self.reuniao_id!r}, membro_id={self.membro_id!r}, status={self.status!r})"
