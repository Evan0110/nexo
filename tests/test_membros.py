from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from app.repository import MembroRepository


def test_criar_e_listar(db_session):
    repo = MembroRepository()
    repo.criar(nome="Alice", matricula="A-001")
    repo.criar(nome="Bob", matricula="B-001")

    membros = repo.listar()
    assert len(membros) == 2
    # listar ordena por nome
    assert [m.nome for m in membros] == ["Alice", "Bob"]


def test_obter(db_session):
    repo = MembroRepository()
    m = repo.criar(nome="Alice")

    recuperado = repo.obter(m.id)
    assert recuperado is not None
    assert recuperado.nome == "Alice"

    assert repo.obter(9999) is None


def test_atualizar(db_session):
    repo = MembroRepository()
    m = repo.criar(nome="Alice", cargo="Membro")

    atualizado = repo.atualizar(
        m.id,
        nome="Alice Silva",
        cargo="Diretor",
        matricula="A-001",
        departamento="Training",
        email="alice@x.com",
        telefone="11999999999",
        data_ingresso=date(2025, 3, 1),
        status="Ativo",
    )
    assert atualizado is not None
    assert atualizado.nome == "Alice Silva"
    assert atualizado.cargo == "Diretor"
    assert atualizado.departamento == "Training"

    # Recarrega do banco para confirmar persistência
    outra_sessao = repo.obter(m.id)
    assert outra_sessao.nome == "Alice Silva"


def test_atualizar_inexistente_retorna_none(db_session):
    repo = MembroRepository()
    assert repo.atualizar(9999, nome="Fantasma") is None


def test_excluir(db_session):
    repo = MembroRepository()
    m = repo.criar(nome="Alice")

    assert repo.excluir(m.id) is True
    assert repo.excluir(m.id) is False  # segunda vez
    assert repo.obter(m.id) is None


def test_email_unico(db_session):
    repo = MembroRepository()
    repo.criar(nome="Alice", email="a@x.com")

    with pytest.raises(IntegrityError):
        repo.criar(nome="Bob", email="a@x.com")


def test_percentual_sem_reunioes(db_session):
    repo = MembroRepository()
    m = repo.criar(nome="Alice")
    assert repo.percentual_presenca(m.id) == 0.0


def test_percentual_50_por_cento(db_session):
    from app.repository import ReuniaoRepository, PresencaRepository

    membros = MembroRepository()
    reunioes = ReuniaoRepository()
    presencas = PresencaRepository()

    m = membros.criar(nome="Alice")
    r1 = reunioes.criar(titulo="R1", data_reuniao=date(2025, 11, 1))
    r2 = reunioes.criar(titulo="R2", data_reuniao=date(2025, 11, 8))

    presencas.registrar(r1.id, m.id, "Presente")
    presencas.registrar(r2.id, m.id, "Ausente")

    assert membros.percentual_presenca(m.id) == 50.0


def test_percentual_justificado_conta(db_session):
    from app.repository import ReuniaoRepository, PresencaRepository

    membros = MembroRepository()
    reunioes = ReuniaoRepository()
    presencas = PresencaRepository()

    m = membros.criar(nome="Alice")
    r1 = reunioes.criar(titulo="R1", data_reuniao=date(2025, 11, 1))
    r2 = reunioes.criar(titulo="R2", data_reuniao=date(2025, 11, 8))

    presencas.registrar(r1.id, m.id, "Justificado")
    presencas.registrar(r2.id, m.id, "Presente")

    # Regra da Liga: Justificado conta como presença
    assert membros.percentual_presenca(m.id) == 100.0


def test_estatisticas_gerais(db_session):
    from app.repository import ReuniaoRepository, PresencaRepository

    membros = MembroRepository()
    reunioes = ReuniaoRepository()
    presencas = PresencaRepository()

    # 3 ativos + 1 inativo
    a = membros.criar(nome="Alice", status="Ativo")
    b = membros.criar(nome="Bob", status="Ativo")
    c = membros.criar(nome="Carol", status="Ativo")
    membros.criar(nome="Inativo", status="Inativo")

    r1 = reunioes.criar(titulo="R1", data_reuniao=date(2025, 11, 1))
    r2 = reunioes.criar(titulo="R2", data_reuniao=date(2025, 11, 8))

    # Alice: 2/2 = 100%
    presencas.registrar(r1.id, a.id, "Presente")
    presencas.registrar(r2.id, a.id, "Presente")
    # Bob: 1/2 = 50% (abaixo de 75)
    presencas.registrar(r1.id, b.id, "Presente")
    # Carol: 0/2 = 0% (abaixo de 75)
    presencas.registrar(r1.id, c.id, "Ausente")

    stats = membros.estatisticas_gerais()
    assert stats["total_ativos"] == 3
    assert stats["total_reunioes"] == 2
    # média = (100 + 50 + 0) / 3 ≈ 50.0
    assert stats["presenca_media"] == 50.0
    # abaixo de 75: Bob (50) e Carol (0), ordenados
    nomes_abaixo = [m["nome"] for m in stats["abaixo_75"]]
    assert nomes_abaixo == ["Carol", "Bob"]
