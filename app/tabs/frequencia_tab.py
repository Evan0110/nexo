from datetime import date

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QComboBox,
    QPushButton,
    QMessageBox,
    QListWidget,
    QListWidgetItem,
    QTableWidget,
    QTableWidgetItem,
    QSplitter,
    QAbstractItemView,
    QDateEdit,
    QFileDialog,
)
from PySide6.QtCore import QDate, Qt

from app.repository import MembroRepository, ReuniaoRepository, PresencaRepository

from app.export import exportar_frequencia_csv

class FrequenciaTab(QWidget):
    def __init__(self):
        super().__init__()
        self.repo_membro = MembroRepository()
        self.repo_reuniao = ReuniaoRepository()
        self.repo_presenca = PresencaRepository()

        self.reuniao_atual_id: int | None = None

        # ---- Formulário de nova reunião ----
        self.input_titulo = QLineEdit()
        self.input_data = QDateEdit()
        self.input_data.setCalendarPopup(True)
        self.input_data.setDate(QDate.currentDate())
        self.input_tipo = QComboBox()
        self.input_tipo.setEditable(True)
        self.input_tipo.addItems(["Geral", "Training", "Projetos", "Assembleia"])

        form = QFormLayout()
        form.addRow("Título:", self.input_titulo)
        form.addRow("Data:", self.input_data)
        form.addRow("Tipo:", self.input_tipo)

        grupo_form = QGroupBox("Nova reunião")
        grupo_form.setLayout(form)

        btn_criar = QPushButton("Criar reunião")
        btn_criar.clicked.connect(self.criar_reuniao)

        btn_excluir_reuniao = QPushButton("Excluir reunião")
        btn_excluir_reuniao.clicked.connect(self.excluir_reuniao)

        btn_exportar = QPushButton("Exportar CSV")
        btn_exportar.clicked.connect(self.exportar_csv)

        barra_form = QHBoxLayout()
        barra_form.addWidget(btn_criar)
        barra_form.addWidget(btn_excluir_reuniao)
        barra_form.addStretch()
        barra_form.addWidget(btn_exportar)

        topo = QVBoxLayout()
        topo.addWidget(grupo_form)
        topo.addLayout(barra_form)

        # ---- Lista de reuniões ----
        self.lista_reunioes = QListWidget()
        self.lista_reunioes.currentItemChanged.connect(self.ao_selecionar_reuniao)

        grupo_lista = QGroupBox("Reuniões")
        vbox_lista = QVBoxLayout()
        vbox_lista.addWidget(self.lista_reunioes)
        grupo_lista.setLayout(vbox_lista)

        # ---- Tabela de presenças ----
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(3)
        self.tabela.setHorizontalHeaderLabels(["Membro", "Status", "% Presença"])
        self.tabela.horizontalHeader().setStretchLastSection(True)
        self.tabela.setColumnWidth(0, 250)
        self.tabela.setColumnWidth(1, 160)
        self.tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        grupo_tabela = QGroupBox("Presenças da reunião selecionada")
        vbox_tabela = QVBoxLayout()
        vbox_tabela.addWidget(self.tabela)
        grupo_tabela.setLayout(vbox_tabela)

        btn_salvar = QPushButton("Salvar presenças")
        btn_salvar.clicked.connect(self.salvar_presencas)

        # ---- Splitter horizontal ----
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(grupo_lista)
        splitter.addWidget(grupo_tabela)
        splitter.setSizes([320, 780])

        # ---- Layout final ----
        layout = QVBoxLayout()
        layout.addLayout(topo)
        layout.addWidget(splitter)
        layout.addWidget(btn_salvar)
        self.setLayout(layout)

        self.carregar_reunioes()

    # ---------- Reuniões ----------

    def carregar_reunioes(self):
        self.lista_reunioes.clear()
        for r in self.repo_reuniao.listar():
            texto = f"{r.data.strftime('%d/%m/%Y')} — {r.titulo} ({r.tipo})"
            item = QListWidgetItem(texto)
            item.setData(Qt.ItemDataRole.UserRole, r.id)
            self.lista_reunioes.addItem(item)

    def criar_reuniao(self):
        titulo = self.input_titulo.text().strip()
        if not titulo:
            QMessageBox.warning(self, "Campo obrigatório", "Informe o título da reunião.")
            return

        qd = self.input_data.date()
        data_reuniao = date(qd.year(), qd.month(), qd.day())
        tipo = self.input_tipo.currentText().strip() or "Geral"

        try:
            self.repo_reuniao.criar(titulo=titulo, data_reuniao=data_reuniao, tipo=tipo)
        except Exception as exc:
            QMessageBox.critical(self, "Erro ao criar", str(exc))
            return

        self.input_titulo.clear()
        self.carregar_reunioes()

    def excluir_reuniao(self):
        item = self.lista_reunioes.currentItem()
        if not item:
            QMessageBox.information(
                self, "Seleção", "Selecione uma reunião para excluir."
            )
            return

        rid = item.data(Qt.ItemDataRole.UserRole)
        confirm = QMessageBox.question(
            self,
            "Confirmar exclusão",
            "Excluir esta reunião e todas as presenças associadas?",
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        self.repo_reuniao.excluir(rid)
        self.reuniao_atual_id = None
        self.tabela.setRowCount(0)
        self.carregar_reunioes()

    def ao_selecionar_reuniao(self, current, previous):
        if current is None:
            self.reuniao_atual_id = None
            self.tabela.setRowCount(0)
            return
        self.reuniao_atual_id = current.data(Qt.ItemDataRole.UserRole)
        self.carregar_presencas()

    # ---------- Presenças ----------

    def carregar_presencas(self):
        if self.reuniao_atual_id is None:
            return

        membros = self.repo_membro.listar_ativos()
        self.tabela.setRowCount(len(membros))

        for i, m in enumerate(membros):
            # Coluna 0: nome (guarda membro_id em UserRole)
            item_nome = QTableWidgetItem(m.nome)
            item_nome.setData(Qt.ItemDataRole.UserRole, m.id)
            self.tabela.setItem(i, 0, item_nome)

            # Coluna 1: combo de status
            combo = QComboBox()
            combo.addItems(["Presente", "Ausente", "Justificado"])
            status_atual = self.repo_presenca.status_de(self.reuniao_atual_id, m.id)
            if status_atual:
                idx = combo.findText(status_atual)
                if idx >= 0:
                    combo.setCurrentIndex(idx)
            self.tabela.setCellWidget(i, 1, combo)

            # Coluna 2: % presença acumulado
            pct = self.repo_membro.percentual_presenca(m.id)
            item_pct = QTableWidgetItem(f"{pct}%")
            item_pct.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabela.setItem(i, 2, item_pct)

    def salvar_presencas(self):
        if self.reuniao_atual_id is None:
            QMessageBox.information(
                self, "Seleção", "Selecione uma reunião primeiro."
            )
            return

        try:
            for i in range(self.tabela.rowCount()):
                item_nome = self.tabela.item(i, 0)
                if not item_nome:
                    continue
                membro_id = item_nome.data(Qt.ItemDataRole.UserRole)
                combo = self.tabela.cellWidget(i, 1)
                if not isinstance(combo, QComboBox):
                    continue
                status = combo.currentText()
                self.repo_presenca.registrar(
                    self.reuniao_atual_id, membro_id, status
                )
        except Exception as exc:
            QMessageBox.critical(self, "Erro ao salvar", str(exc))
            return

        QMessageBox.information(self, "Sucesso", "Presenças salvas!")
        self.carregar_presencas()  # atualiza os %

    def exportar_csv(self):
        caminho, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar frequência para CSV",
            "frequencia.csv",
            "CSV (*.csv)",
        )
        if not caminho:
            return
        try:
            info = exportar_frequencia_csv(caminho)
        except Exception as exc:
            QMessageBox.critical(self, "Erro ao exportar", str(exc))
            return

        msg = (
            f"Exportação concluída!\n\n"
            f"Reuniões: {info['reunioes']}\n"
            f"Membros: {info['membros']}\n\n"
            f"Arquivos gerados:\n" + "\n".join(info["arquivos"])
        )
        QMessageBox.information(self, "Exportação concluída", msg)
