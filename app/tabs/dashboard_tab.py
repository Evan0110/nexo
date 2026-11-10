from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGroupBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from app.repository import MembroRepository


class DashboardTab(QWidget):
    def __init__(self):
        super().__init__()
        self.repo = MembroRepository()

        # ---- KPI cards ----
        self.kpi_ativos = self._criar_kpi("Membros ativos")
        self.kpi_reunioes = self._criar_kpi("Reuniões registradas")
        self.kpi_media = self._criar_kpi("Presença média")

        barra_kpis = QHBoxLayout()
        barra_kpis.addWidget(self.kpi_ativos["card"])
        barra_kpis.addWidget(self.kpi_reunioes["card"])
        barra_kpis.addWidget(self.kpi_media["card"])

        # ---- Alerta ----
        self.label_alerta = QLabel("")
        self.label_alerta.setStyleSheet("font-size: 14px; padding: 6px;")

        # ---- Tabela de membros abaixo de 75% ----
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(3)
        self.tabela.setHorizontalHeaderLabels(["Nome", "Matrícula", "% Presença"])
        self.tabela.horizontalHeader().setStretchLastSection(True)
        self.tabela.setColumnWidth(0, 300)
        self.tabela.setColumnWidth(1, 150)
        self.tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        grupo_tabela = QGroupBox("Membros abaixo de 75% de presença")
        vbox_tabela = QVBoxLayout()
        vbox_tabela.addWidget(self.tabela)
        grupo_tabela.setLayout(vbox_tabela)

        # ---- Botão ----
        btn_refresh = QPushButton("Atualizar dashboard")
        btn_refresh.clicked.connect(self.atualizar)

        # ---- Layout final ----
        layout = QVBoxLayout()
        layout.addLayout(barra_kpis)
        layout.addWidget(self.label_alerta)
        layout.addWidget(grupo_tabela)
        layout.addWidget(btn_refresh)
        self.setLayout(layout)

        self.atualizar()

    def _criar_kpi(self, titulo: str) -> dict:
        card = QGroupBox(titulo)
        card.setStyleSheet("QGroupBox { font-weight: bold; font-size: 13px; }")
        vbox = QVBoxLayout()
        valor_label = QLabel("0")
        f = QFont()
        f.setPointSize(28)
        f.setBold(True)
        valor_label.setFont(f)
        valor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vbox.addWidget(valor_label)
        card.setLayout(vbox)
        return {"card": card, "valor": valor_label}

    def atualizar(self):
        stats = self.repo.estatisticas_gerais()

        self.kpi_ativos["valor"].setText(str(stats["total_ativos"]))
        self.kpi_reunioes["valor"].setText(str(stats["total_reunioes"]))
        self.kpi_media["valor"].setText(f"{stats['presenca_media']}%")

        membros = stats["abaixo_75"]
        if membros:
            self.label_alerta.setText(
                f"⚠️  {len(membros)} membro(s) abaixo da meta de 75%."
            )
            self.label_alerta.setStyleSheet(
                "font-size: 14px; padding: 6px; color: #b00020;"
            )
        else:
            self.label_alerta.setText("✅ Todos os membros ativos estão na meta.")
            self.label_alerta.setStyleSheet(
                "font-size: 14px; padding: 6px; color: #1b5e20;"
            )

        self.tabela.setRowCount(len(membros))
        for i, m in enumerate(membros):
            self.tabela.setItem(i, 0, QTableWidgetItem(m["nome"]))
            self.tabela.setItem(i, 1, QTableWidgetItem(m["matricula"] or "—"))
            item_pct = QTableWidgetItem(f"{m['percentual']}%")
            item_pct.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_pct.setForeground(Qt.GlobalColor.red)
            self.tabela.setItem(i, 2, item_pct)
