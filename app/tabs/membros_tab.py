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
)
from PySide6.QtCore import QDate
from PySide6.QtSql import QSqlTableModel

from app.repository import MembroRepository


class MembrosTab(QWidget):
    def __init__(self):
        super().__init__()
        self.repo = MembroRepository()

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

        grupo_form = QGroupBox("Novo membro")
        grupo_form.setLayout(form)

        # ---- Botões ----
        btn_add = QPushButton("Adicionar")
        btn_add.clicked.connect(self.adicionar_membro)

        btn_del = QPushButton("Excluir selecionado")
        btn_del.clicked.connect(self.excluir_membro)

        btn_refresh = QPushButton("Atualizar")
        btn_refresh.clicked.connect(self.recarregar)

        barra_botoes = QHBoxLayout()
        barra_botoes.addWidget(btn_add)
        barra_botoes.addWidget(btn_del)
        barra_botoes.addWidget(btn_refresh)
        barra_botoes.addStretch()

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

        # ---- Layout ----
        layout = QVBoxLayout()
        layout.addWidget(grupo_form)
        layout.addLayout(barra_botoes)
        layout.addWidget(self.view)
        self.setLayout(layout)

    def recarregar(self):
        self.model.select()

    def adicionar_membro(self):
        nome = self.input_nome.text().strip()
        if not nome:
            QMessageBox.warning(self, "Campo obrigatório", "Informe o nome do membro.")
            return

        qdate = self.input_data_ingresso.date()
        data_ing = date(qdate.year(), qdate.month(), qdate.day())

        try:
            self.repo.criar(
                nome=nome,
                matricula=self.input_matricula.text().strip() or None,
                cargo=self.input_cargo.currentText().strip() or None,
                departamento=self.input_departamento.currentText().strip() or None,
                email=self.input_email.text().strip() or None,
                telefone=self.input_telefone.text().strip() or None,
                data_ingresso=data_ing,
                status=self.input_status.currentText(),
            )
        except Exception as exc:
            QMessageBox.critical(self, "Erro ao salvar", str(exc))
            return

        self.input_nome.clear()
        self.input_matricula.clear()
        self.input_email.clear()
        self.input_telefone.clear()
        self.input_nome.setFocus()
        self.recarregar()

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
        self.recarregar()
