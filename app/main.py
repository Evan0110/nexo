import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTableView,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QWidget,
    QGroupBox,
    QLineEdit,
    QComboBox,
    QPushButton,
    QMessageBox,
    QAbstractItemView,
)
from PySide6.QtSql import QSqlDatabase, QSqlTableModel

from app.database import DB_PATH
from app.repository import MembroRepository


class JanelaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("nexo — Sistema de RH")
        self.repo = MembroRepository()

        # Conexão do Qt com o SQLite (só para exibição)
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName(str(DB_PATH))
        if not db.open():
            QMessageBox.critical(self, "Erro", "Não foi possível abrir o banco.")
            sys.exit(1)

        # ---- Formulário de cadastro ----
        self.input_nome = QLineEdit()
        self.input_cargo = QComboBox()
        self.input_cargo.setEditable(True)
        self.input_cargo.addItems(["Diretor", "Membro", "Trainee", "Externo"])
        self.input_email = QLineEdit()
        self.input_status = QComboBox()
        self.input_status.addItems(["Ativo", "Inativo", "Egresso"])

        form = QFormLayout()
        form.addRow("Nome:", self.input_nome)
        form.addRow("Cargo:", self.input_cargo)
        form.addRow("Email:", self.input_email)
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

        # ---- Layout final ----
        layout = QVBoxLayout()
        layout.addWidget(grupo_form)
        layout.addLayout(barra_botoes)
        layout.addWidget(self.view)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def recarregar(self):
        self.model.select()

    def adicionar_membro(self):
        nome = self.input_nome.text().strip()
        if not nome:
            QMessageBox.warning(self, "Campo obrigatório", "Informe o nome do membro.")
            return

        try:
            self.repo.criar(
                nome=nome,
                cargo=self.input_cargo.currentText().strip() or None,
                email=self.input_email.text().strip() or None,
                status=self.input_status.currentText(),
            )
        except Exception as exc:
            QMessageBox.critical(self, "Erro ao salvar", str(exc))
            return

        self.input_nome.clear()
        self.input_email.clear()
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


def main() -> None:
    app = QApplication(sys.argv)
    janela = JanelaPrincipal()
    janela.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
