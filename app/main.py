import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QMessageBox
from PySide6.QtSql import QSqlDatabase

from app.database import DB_PATH
from app.tabs.membros_tab import MembrosTab
from app.tabs.frequencia_tab import FrequenciaTab


class JanelaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("nexo — Sistema de RH")
        self.resize(1100, 720)

        # Conexão Qt SQL — usada pela aba Membros (QSqlTableModel)
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(str(DB_PATH))
        if not self.db.open():
            QMessageBox.critical(self, "Erro", "Não foi possível abrir o banco.")
            sys.exit(1)

        tabs = QTabWidget()
        tabs.addTab(MembrosTab(), "Membros")
        tabs.addTab(FrequenciaTab(), "Frequência")
        self.setCentralWidget(tabs)


def main() -> None:
    app = QApplication(sys.argv)
    janela = JanelaPrincipal()
    janela.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

