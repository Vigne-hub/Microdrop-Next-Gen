import sys
from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QMessageBox, QLabel


class GUI(QWidget):
    def __init__(self, orchestrator, backend_queues, title):
        super().__init__()
        self.orchestrator = orchestrator
        self.backend_queues = backend_queues
        self.gui_id = self.orchestrator.register_gui(self)
        self.init_ui(title)

    def init_ui(self, title):
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 200, 100)
        layout = QVBoxLayout()

        self.button1 = QPushButton("Send to Backend 1")
        self.button1.clicked.connect(lambda: self.send_task(1))
        layout.addWidget(self.button1)

        self.button2 = QPushButton("Send to Backend 2")
        self.button2.clicked.connect(lambda: self.send_task(2))
        layout.addWidget(self.button2)

        self.result_box = QLabel("N/A")
        layout.addWidget(self.result_box)

        self.setLayout(layout)
        self.show()

    def send_task(self, backend_num):
        task = {"task": f"Task from {self.windowTitle()} to Backend {backend_num}", "gui_id": self.gui_id}
        self.orchestrator.send_task(task, self.backend_queues[backend_num - 1])

    def display_result(self, message):
        self.result_box.setText(message)
