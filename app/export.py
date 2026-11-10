from pathlib import Path

import pandas as pd

from app import database
from app.models import Membro, Reuniao, Presenca


def exportar_membros_csv(caminho: str | Path) -> int:
    """Exporta todos os membros para CSV. Retorna o número de linhas."""
    with database.SessionLocal() as session:
        membros = session.query(Membro).order_by(Membro.nome).all()

    dados = [
        {
            "ID": m.id,
            "Nome": m.nome,
            "Matrícula": m.matricula or "",
            "Cargo": m.cargo or "",
            "Departamento": m.departamento or "",
            "Email": m.email or "",
            "Telefone": m.telefone or "",
            "Data de ingresso": m.data_ingresso.isoformat() if m.data_ingresso else "",
            "Status": m.status,
        }
        for m in membros
    ]

    df = pd.DataFrame(dados)
    df.to_csv(caminho, index=False, encoding="utf-8-sig")
    return len(df)


def exportar_frequencia_csv(caminho: str | Path) -> dict:
    """Exporta matriz de presenças + resumo de %.

    Retorna {'reunioes': N, 'membros': N, 'resumo': {nome: pct}}.
    """
    with database.SessionLocal() as session:
        membros = (
            session.query(Membro)
            .filter(Membro.status == "Ativo")
            .order_by(Membro.nome)
            .all()
        )
        reunioes = session.query(Reuniao).order_by(Reuniao.data).all()

        # Matriz: linhas = membros, colunas = reuniões
        matriz = []
        for m in membros:
            linha = {"Membro": m.nome, "Matrícula": m.matricula or ""}
            for r in reunioes:
                p = (
                    session.query(Presenca)
                    .filter(
                        Presenca.reuniao_id == r.id,
                        Presenca.membro_id == m.id,
                    )
                    .one_or_none()
                )
                coluna = f"{r.data.strftime('%d/%m')} — {r.titulo}"
                linha[coluna] = p.status if p else "—"
            matriz.append(linha)

        # Resumo: % por membro
        total_reunioes = len(reunioes)
        resumo = []
        for m in membros:
            if total_reunioes == 0:
                pct = 0.0
            else:
                compareceu = (
                    session.query(Presenca)
                    .filter(
                        Presenca.membro_id == m.id,
                        Presenca.status.in_(["Presente", "Justificado"]),
                    )
                    .count()
                )
                pct = round((compareceu / total_reunioes) * 100, 1)

            resumo.append(
                {
                    "Membro": m.nome,
                    "Matrícula": m.matricula or "",
                    "Presenças": sum(
                        1
                        for linha in matriz
                        if linha["Membro"] == m.nome
                        for k, v in linha.items()
                        if k not in ("Membro", "Matrícula")
                        and v in ("Presente", "Justificado")
                    ),
                    "Total de reuniões": total_reunioes,
                    "% Presença": pct,
                }
            )

    # Dois CSVs separados (mais fácil de importar no Excel)
    caminho = Path(caminho)
    df_matriz = pd.DataFrame(matriz)
    df_resumo = pd.DataFrame(resumo)

    df_matriz.to_csv(
        caminho.with_name(caminho.stem + "_matriz.csv"),
        index=False,
        encoding="utf-8-sig",
    )
    df_resumo.to_csv(
        caminho.with_name(caminho.stem + "_resumo.csv"),
        index=False,
        encoding="utf-8-sig",
    )

    return {
        "reunioes": total_reunioes,
        "membros": len(membros),
        "arquivos": [
            str(caminho.with_name(caminho.stem + "_matriz.csv")),
            str(caminho.with_name(caminho.stem + "_resumo.csv")),
        ],
    }
