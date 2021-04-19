import variables
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QLineEdit,
    QLabel,
    QListWidget,
)

class DialogList(QWidget):
    def __init__(self):
        super(DialogList, self).__init__()
        self.main_layout = QVBoxLayout()
        self.add_layout = QHBoxLayout()
        self.dialogs = QListWidget()
        self.ip_label = QLabel("IP:")
        self.ip_label.setFont(variables.font)
        self.ip_input = QLineEdit()
        self.ip_input.setFont(variables.font)
        self.add_btn = QPushButton("Add")
        self.add_btn.setStyleSheet("font: 14pt Lobster;")
        self.add_btn.pressed.connect(self.add_dialog)
        self.error_label = QLabel(" ")
        self.error_label.setStyleSheet("color: red; font: 14pt Lobster;")
        self.main_layout.addWidget(self.dialogs)
        self.add_layout.addWidget(self.ip_label)
        self.add_layout.addWidget(self.ip_input)
        self.add_layout.addWidget(self.add_btn)
        self.main_layout.addWidget(self.error_label)
        self.main_layout.addLayout(self.add_layout)
        self.setLayout(self.main_layout)

    def add_dialog(self):
        ip = self.ip_input.text()
        print(type(ip))
        self.error_label.setText("")
        if variables.nw.connect_to(ip):
            pass
        else:
            self.error_label.setText("Error occurred")
