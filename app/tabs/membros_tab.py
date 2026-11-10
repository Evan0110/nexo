from datetime import date

from PySide6.QtWidgets import (
    QWidget,
    QTableView,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QComboBox,
    QPushButton,
    QMessageBox,
    QAbstractItemView,
    QDateEdit,
    QLabel,
    QFileDialog,
)
from PySide6.QtCore import QDate
from PySide6.QtSql import QSqlTableModel

from app.repository import MembroRepository
from app.export import exportar_membros_csv


class MembrosTab(QWidget):
    def __init__(self):
        super().__init__()
        self.repo = MembroRepository()
        self.membro_em_edicao_id: int | None = None

        # ---- Formulário ----
        self.input_nome = QLineEdit()
        self.input_matricula = QLineEdit()
        self.input_cargo = QComboBox()
        self.input_cargo.setEditable(True)
        self.input_cargo.addItems(["Diretor", "Membro", "Trainee", "Externo"])
        self.input_departamento = QComboBox()
        self.input_departamento.setEditable(True)
        self.input_departamento.addItems(["Training", "Marketing", "RH", "Projetos"])
        self.input_email = QLineEdit()
        self.input_telefone = QLineEdit()
        self.input_data_ingresso = QDateEdit()
        self.input_data_ingresso.setCalendarPopup(True)
        self.input_data_ingresso.setDate(QDate.currentDate())
        self.input_status = QComboBox()
        self.input_status.addItems(["Ativo", "Inativo", "Egresso"])

        form = QFormLayout()
        form.addRow("Nome:", self.input_nome)
        form.addRow("Matrícula:", self.input_matricula)
        form.addRow("Cargo:", self.input_cargo)
        form.addRow("Departamento:", self.input_departamento)
        form.addRow("Email:", self.input_email)
        form.addRow("Telefone:", self.input_telefone)
        form.addRow("Data de ingresso:", self.input_data_ingresso)
        form.addRow("Status:", self.input_status)

        grupo_form = QGroupBox("Cadastro de membro")
        grupo_form.setLayout(form)

        # ---- Label de modo ----
        self.label_modo = QLabel("")
        self.label_modo.setStyleSheet("color: #555; font-style: italic;")

        # ---- Botões ----
        self.btn_add = QPushButton("Adicionar")
        self.btn_add.clicked.connect(self.acao_principal)

        self.btn_cancelar = QPushButton("Cancelar edição")
        self.btn_cancelar.clicked.connect(self.cancelar_edicao)
        self.btn_cancelar.setVisible(False)

        btn_del = QPushButton("Excluir selecionado")
        btn_del.clicked.connect(self.excluir_membro)

        btn_refresh = QPushButton("Atualizar")
        btn_refresh.clicked.connect(self.recarregar)

        btn_exportar = QPushButton("Exportar CSV")
        btn_exportar.clicked.connect(self.exportar_csv)


        barra_botoes = QHBoxLayout()
        barra_botoes.addWidget(self.btn_add)
        barra_botoes.addWidget(self.btn_cancelar)
        barra_botoes.addWidget(btn_del)
        barra_botoes.addWidget(btn_refresh)
        barra_botoes.addStretch()
        barra_botoes.addWidget(btn_refresh)
        barra_botoes.addWidget(btn_exportar)

        # ---- Tabela ----
        self.model = QSqlTableModel()
        self.model.setTable("membros")
        self.model.select()

        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.setAlternatingRowColors(True)
        self.view.horizontalHeader().setStretchLastSection(True)
        self.view.setColumnHidden(0, True)
        self.view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.view.doubleClicked.connect(self.carregar_para_edicao)

        # ---- Layout ----
        layout = QVBoxLayout()
        layout.addWidget(grupo_form)
        layout.addWidget(self.label_modo)
        layout.addLayout(barra_botoes)
        layout.addWidget(self.view)
        self.setLayout(layout)

    def recarregar(self):
        self.model.select()

    def _coletar_dados(self) -> dict | None:
        """Coleta e valida os dados do formulário. Retorna None se inválido."""
        nome = self.input_nome.text().strip()
        if not nome:
            QMessageBox.warning(self, "Campo obrigatório", "Informe o nome do membro.")
            return None

        qd = self.input_data_ingresso.date()
        data_ing = date(qd.year(), qd.month(), qd.day())

        return {
            "nome": nome,
            "matricula": self.input_matricula.text().strip() or None,
            "cargo": self.input_cargo.currentText().strip() or None,
            "departamento": self.input_departamento.currentText().strip() or None,
            "email": self.input_email.text().strip() or None,
            "telefone": self.input_telefone.text().strip() or None,
            "data_ingresso": data_ing,
            "status": self.input_status.currentText(),
        }

    def acao_principal(self):
        """Dispatch: cria novo ou salva edição, dependendo do modo."""
        dados = self._coletar_dados()
        if dados is None:
            return

        try:
            if self.membro_em_edicao_id is not None:
                self.repo.atualizar(self.membro_em_edicao_id, **dados)
                QMessageBox.information(self, "Sucesso", "Membro atualizado!")
            else:
                self.repo.criar(**dados)
        except Exception as exc:
            QMessageBox.critical(self, "Erro ao salvar", str(exc))
            return

        self.limpar_form()
        self.recarregar()

    def limpar_form(self):
        self.input_nome.clear()
        self.input_matricula.clear()
        self.input_cargo.setEditText("")
        self.input_departamento.setEditText("")
        self.input_email.clear()
        self.input_telefone.clear()
        self.input_data_ingresso.setDate(QDate.currentDate())
        self.input_status.setCurrentIndex(0)

        self.membro_em_edicao_id = None
        self.btn_add.setText("Adicionar")
        self.btn_cancelar.setVisible(False)
        self.label_modo.setText("")
        self.input_nome.setFocus()

    def carregar_para_edicao(self, index):
        """Duplo-clique na tabela: carrega membro no formulário."""
        membro_id_raw = self.model.data(self.model.index(index.row(), 0))
        if membro_id_raw is None:
            return

        membro_id = int(membro_id_raw)
        m = self.repo.obter(membro_id)
        if not m:
            QMessageBox.warning(self, "Erro", "Membro não encontrado.")
            return

        self.membro_em_edicao_id = membro_id

        self.input_nome.setText(m.nome)
        self.input_matricula.setText(m.matricula or "")
        self.input_cargo.setEditText(m.cargo or "")
        self.input_departamento.setEditText(m.departamento or "")
        self.input_email.setText(m.email or "")
        self.input_telefone.setText(m.telefone or "")
        if m.data_ingresso:
            qd = QDate(m.data_ingresso.year, m.data_ingresso.month, m.data_ingresso.day)
            self.input_data_ingresso.setDate(qd)
        self.input_status.setCurrentText(m.status)

        self.btn_add.setText("Salvar alterações")
        self.btn_cancelar.setVisible(True)
        self.label_modo.setText(f"Editando: {m.nome} (ID {m.id})")

    def cancelar_edicao(self):
        self.limpar_form()

    def exportar_csv(self):
        caminho, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar membros para CSV",
            "membros.csv",
            "CSV (*.csv)",
        )
        if not caminho:
            return
        try:
            n = exportar_membros_csv(caminho)
        except Exception as exc:
            QMessageBox.critical(self, "Erro ao exportar", str(exc))
            return
        QMessageBox.information(
            self, "Exportação concluída", f"{n} membro(s) exportados para:\n{caminho}"
        )

    def excluir_membro(self):
        idx = self.view.currentIndex()
        if not idx.isValid():
            QMessageBox.information(self, "Seleção", "Selecione uma linha para excluir.")
            return

        membro_id = self.model.data(self.model.index(idx.row(), 0))
        confirm = QMessageBox.question(
            self, "Confirmar exclusão", f"Excluir o membro de ID {membro_id}?"
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        self.repo.excluir(int(membro_id))
        if self.membro_em_edicao_id is not None:
            self.limpar_form()
        self.recarregar()
