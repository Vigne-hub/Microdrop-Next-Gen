import json
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, \
    QComboBox, QMessageBox
import requests


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Task Orchestrator Frontend")
        self.setGeometry(100, 100, 400, 200)

        # Main widget and layout
        widget = QWidget()
        layout = QVBoxLayout()

        # Input for Task Type
        self.task_type_input = QLineEdit()
        self.task_type_input.setPlaceholderText("Enter task type")
        layout.addWidget(self.task_type_input)

        # Dropdown for Backend Type
        self.backend_selector = QComboBox()
        self.backend_selector.addItems(["hardware", "database", "analytics"])
        layout.addWidget(self.backend_selector)

        # Input for Data Parameters
        self.data_input = QLineEdit()
        self.data_input.setPlaceholderText("Enter data parameters as JSON")
        layout.addWidget(self.data_input)

        # Submit Button
        submit_button = QPushButton("Submit Task")
        submit_button.clicked.connect(self.submit_task)
        layout.addWidget(submit_button)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def submit_task(self):
        task_type = self.task_type_input.text()
        backend_type = self.backend_selector.currentText()
        data = self.data_input.text()

        try:
            data_json = json.loads(data)  # Ensure data is valid JSON
            response = requests.post("http://localhost:8001/orchestrate/", json={
                "backend_type": backend_type,
                "task_type": task_type,
                "data": data_json
            })
            response.raise_for_status()
            QMessageBox.information(self, "Task Submission", "Task submitted successfully!")
        except requests.RequestException as e:
            QMessageBox.critical(self, "Error", f"Failed to submit task: {e}")
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Error", "Invalid JSON data.")

        self.task_type_input.clear()
        self.data_input.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
