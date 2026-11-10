from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class FrequenciaTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        placeholder = QLabel("Módulo de Frequência — em construção (B.3)")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(placeholder)
        self.setLayout(layout)
