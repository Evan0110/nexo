from datetime import date

from sqlalchemy import func

from app import database
from app.models import Membro, Reuniao, Presenca


class MembroRepository:
    """Camada de acesso a dados de membros."""

    def listar(self) -> list[Membro]:
        with database.SessionLocal() as session:
            return session.query(Membro).order_by(Membro.nome).all()

    def listar_ativos(self) -> list[Membro]:
        with database.SessionLocal() as session:
            return (
                session.query(Membro)
                .filter(Membro.status == "Ativo")
                .order_by(Membro.nome)
                .all()
            )

    def obter(self, membro_id: int) -> Membro | None:
        with database.SessionLocal() as session:
            return session.get(Membro, membro_id)

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
        with database.SessionLocal() as session:
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

    def atualizar(
        self,
        membro_id: int,
        nome: str,
        matricula: str | None = None,
        cargo: str | None = None,
        departamento: str | None = None,
        email: str | None = None,
        telefone: str | None = None,
        data_ingresso: date | None = None,
        status: str = "Ativo",
    ) -> Membro | None:
        with database.SessionLocal() as session:
            membro = session.get(Membro, membro_id)
            if not membro:
                return None
            membro.nome = nome
            membro.matricula = matricula
            membro.cargo = cargo
            membro.departamento = departamento
            membro.email = email
            membro.telefone = telefone
            membro.data_ingresso = data_ingresso
            membro.status = status
            session.commit()
            session.refresh(membro)
            return membro

    def excluir(self, membro_id: int) -> bool:
        with database.SessionLocal() as session:
            membro = session.get(Membro, membro_id)
            if not membro:
                return False
            session.delete(membro)
            session.commit()
            return True

    def percentual_presenca(self, membro_id: int) -> float:
        """% de presenca do membro em relacao ao total de reunioes registradas.

        Conta 'Presente' e 'Justificado' como presenca (regra da Liga).
        Retorna 0.0 se nao houver reunioes registradas.
        """
        with database.SessionLocal() as session:
            total = session.query(func.count(Reuniao.id)).scalar() or 0
            if total == 0:
                return 0.0
            compareceu = (
                session.query(func.count(Presenca.id))
                .filter(
                    Presenca.membro_id == membro_id,
                    Presenca.status.in_(["Presente", "Justificado"]),
                )
                .scalar()
                or 0
            )
            return round((compareceu / total) * 100, 1)



    def estatisticas_gerais(self) -> dict:
        """KPIs para o dashboard: totais + lista de membros abaixo de 75%."""
        with database.SessionLocal() as session:
            total_ativos = (
                session.query(func.count(Membro.id))
                .filter(Membro.status == "Ativo")
                .scalar()
                or 0
            )
            total_reunioes = session.query(func.count(Reuniao.id)).scalar() or 0

            if total_reunioes == 0:
                return {
                    "total_ativos": total_ativos,
                    "total_reunioes": 0,
                    "presenca_media": 0.0,
                    "abaixo_75": [],
                }

            membros_ativos = (
                session.query(Membro).filter(Membro.status == "Ativo").all()
            )

            percentuais = []
            abaixo_75 = []
            for m in membros_ativos:
                compareceu = (
                    session.query(func.count(Presenca.id))
                    .filter(
                        Presenca.membro_id == m.id,
                        Presenca.status.in_(["Presente", "Justificado"]),
                    )
                    .scalar()
                    or 0
                )
                pct = round((compareceu / total_reunioes) * 100, 1)
                percentuais.append(pct)
                if pct < 75.0:
                    abaixo_75.append(
                        {
                            "id": m.id,
                            "nome": m.nome,
                            "matricula": m.matricula,
                            "percentual": pct,
                        }
                    )

            presenca_media = (
                round(sum(percentuais) / len(percentuais), 1)
                if percentuais
                else 0.0
            )
            abaixo_75.sort(key=lambda x: x["percentual"])

            return {
                "total_ativos": total_ativos,
                "total_reunioes": total_reunioes,
                "presenca_media": presenca_media,
                "abaixo_75": abaixo_75,
            }


class ReuniaoRepository:
    """Camada de acesso a dados de reunioes."""

    def listar(self) -> list[Reuniao]:
        with database.SessionLocal() as session:
            return session.query(Reuniao).order_by(Reuniao.data.desc()).all()

    def criar(self, titulo: str, data_reuniao: date, tipo: str = "Geral") -> Reuniao:
        with database.SessionLocal() as session:
            reuniao = Reuniao(titulo=titulo, data=data_reuniao, tipo=tipo)
            session.add(reuniao)
            session.commit()
            session.refresh(reuniao)
            return reuniao

    def excluir(self, reuniao_id: int) -> bool:
        with database.SessionLocal() as session:
            reuniao = session.get(Reuniao, reuniao_id)
            if not reuniao:
                return False
            session.query(Presenca).filter(Presenca.reuniao_id == reuniao_id).delete()
            session.delete(reuniao)
            session.commit()
            return True


class PresencaRepository:
    """Camada de acesso a dados de presencas."""

    def registrar(
        self, reuniao_id: int, membro_id: int, status: str = "Presente"
    ) -> Presenca:
        """Cria ou atualiza a presenca (upsert manual)."""
        with database.SessionLocal() as session:
            existente = (
                session.query(Presenca)
                .filter(
                    Presenca.reuniao_id == reuniao_id,
                    Presenca.membro_id == membro_id,
                )
                .one_or_none()
            )
            if existente:
                existente.status = status
                session.commit()
                session.refresh(existente)
                return existente

            presenca = Presenca(
                reuniao_id=reuniao_id, membro_id=membro_id, status=status
            )
            session.add(presenca)
            session.commit()
            session.refresh(presenca)
            return presenca

    def listar_por_reuniao(self, reuniao_id: int) -> list[Presenca]:
        with database.SessionLocal() as session:
            return (
                session.query(Presenca)
                .filter(Presenca.reuniao_id == reuniao_id)
                .all()
            )

    def status_de(self, reuniao_id: int, membro_id: int) -> str | None:
        with database.SessionLocal() as session:
            p = (
                session.query(Presenca)
                .filter(
                    Presenca.reuniao_id == reuniao_id,
                    Presenca.membro_id == membro_id,
                )
                .one_or_none()
            )
            return p.status if p else None
