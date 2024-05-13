import sys
import json

import requests
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QTextEdit, QLabel


class TaskSubmitter(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Task Dispatcher')
        self.setGeometry(100, 100, 400, 200)

        # Layout
        layout = QVBoxLayout()

        # Input for method name
        self.method_name = QLineEdit(self)
        self.method_name.setPlaceholderText("Enter task method name")
        layout.addWidget(QLabel("Method Name:"))
        layout.addWidget(self.method_name)

        # Input for parameters as JSON
        self.parameters_input = QTextEdit(self)
        self.parameters_input.setPlaceholderText('Enter parameters in JSON format')
        layout.addWidget(QLabel("Parameters (JSON):"))
        layout.addWidget(self.parameters_input)

        # Submit button
        self.submit_button = QPushButton('Submit Task', self)
        self.submit_button.clicked.connect(self.submit_task)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def submit_task(self):
        method = self.method_name.text()
        try:
            parameters = json.loads(self.parameters_input.toPlainText())
        except json.JSONDecodeError:
            print("Invalid JSON")
            return

        task_info = {
            "method": method,
            "parameters": parameters
            # backend add later
        }

        # Endpoint of the orchestrator
        url = 'http://localhost:8001/dispatch_task/'

        # Sending POST request to the orchestrator
        response = requests.post(url, json=task_info)
        print(response.text)  # Print the response from the server

    def receive_response(self):
        # use rabbitmq to receive tasks from orchestrator and update GUI
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = TaskSubmitter()
    ex.show()
    sys.exit(app.exec())
