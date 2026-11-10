from datetime import date

from app.models import Presenca
from app.repository import MembroRepository, ReuniaoRepository, PresencaRepository


def test_criar_e_listar_reuniao(db_session):
    repo = ReuniaoRepository()
    repo.criar(titulo="Geral", data_reuniao=date(2025, 11, 1), tipo="Geral")
    repo.criar(titulo="Training", data_reuniao=date(2025, 11, 8), tipo="Training")

    reunioes = repo.listar()
    assert len(reunioes) == 2
    # listar ordena por data desc
    assert reunioes[0].titulo == "Training"


def test_registrar_cria_e_atualiza(db_session):
    membros = MembroRepository()
    reunioes = ReuniaoRepository()
    presencas = PresencaRepository()

    m = membros.criar(nome="Alice")
    r = reunioes.criar(titulo="R1", data_reuniao=date(2025, 11, 1))

    # Primeira vez: cria
    p1 = presencas.registrar(r.id, m.id, "Presente")
    assert p1.status == "Presente"
    assert presencas.status_de(r.id, m.id) == "Presente"

    # Segunda vez: atualiza (não duplica)
    p2 = presencas.registrar(r.id, m.id, "Ausente")
    assert p2.id == p1.id  # mesmo registro
    assert p2.status == "Ausente"

    # Não há duplicata na tabela
    total = db_session().query(Presenca).count()
    assert total == 1


def test_status_de_inexistente(db_session):
    membros = MembroRepository()
    reunioes = ReuniaoRepository()
    presencas = PresencaRepository()

    m = membros.criar(nome="Alice")
    r = reunioes.criar(titulo="R1", data_reuniao=date(2025, 11, 1))

    assert presencas.status_de(r.id, m.id) is None


def test_excluir_reuniao_cascata(db_session):
    membros = MembroRepository()
    reunioes = ReuniaoRepository()
    presencas = PresencaRepository()

    m = membros.criar(nome="Alice")
    r = reunioes.criar(titulo="R1", data_reuniao=date(2025, 11, 1))
    presencas.registrar(r.id, m.id, "Presente")

    assert len(presencas.listar_por_reuniao(r.id)) == 1

    assert reunioes.excluir(r.id) is True

    # Presenças associadas foram removidas
    assert len(presencas.listar_por_reuniao(r.id)) == 0
    # Membro continua vivo
    assert membros.obter(m.id) is not None
