from app.repository import MembroRepository


def test_criar_e_listar_membro(db_session):
    repo = MembroRepository()
    m = repo.criar(nome="Alice", matricula="A-001")

    assert m.id is not None
    assert m.nome == "Alice"

    membros = repo.listar()
    assert len(membros) == 1
    assert membros[0].nome == "Alice"
