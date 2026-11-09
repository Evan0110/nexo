from app.database import SessionLocal
from app.models import Membro


class MembroRepository:
    """Camada de acesso a dados de membros. A UI nao fala com o banco direto."""

    def listar(self) -> list[Membro]:
        with SessionLocal() as session:
            return session.query(Membro).order_by(Membro.nome).all()

    def criar(
        self,
        nome: str,
        cargo: str | None,
        email: str | None,
        status: str,
    ) -> Membro:
        with SessionLocal() as session:
            membro = Membro(nome=nome, cargo=cargo, email=email, status=status)
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
