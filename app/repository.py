from datetime import date

from app.database import SessionLocal
from app.models import Membro


class MembroRepository:
    """Camada de acesso a dados de membros."""

    def listar(self) -> list[Membro]:
        with SessionLocal() as session:
            return session.query(Membro).order_by(Membro.nome).all()

    def criar(
        self,
        nome: str,
        matricula: str | None = None,
        cargo: str | None = None,
        departamento: str | None = None,
        email: str | None = None,
        telefone: str | None = None,
        data_ingresso: date | None = None,
        status: str = "Ativo",
    ) -> Membro:
        with SessionLocal() as session:
            membro = Membro(
                nome=nome,
                matricula=matricula,
                cargo=cargo,
                departamento=departamento,
                email=email,
                telefone=telefone,
                data_ingresso=data_ingresso,
                status=status,
            )
            session.add(membro)
            session.commit()
            session.refresh(membro)
            return membro

    def excluir(self, membro_id: int) -> bool:
        with SessionLocal() as session:
            membro = session.get(Membro, membro_id)
            if not membro:
                return False
            session.delete(membro)
            session.commit()
            return True
