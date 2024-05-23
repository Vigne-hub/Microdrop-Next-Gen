import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem
from PySide6.QtCore import QTimer

class TableController(QWidget):
    def __init__(self):
        super().__init__()
        self.timer = QTimer(self)
        self.is_running = False
        self.current_row = 0
        self.init_ui()

    def init_ui(self):
        # Layouts
        self.layout = QVBoxLayout(self)
        self.button_layout = QHBoxLayout()

        # Table setup
        self.table = QTableWidget(5, 3)  # 5 rows and 3 columns
        self.table.setHorizontalHeaderLabels(['Description', 'Value', 'Duration (s)'])
        for i in range(5):
            self.table.setItem(i, 0, QTableWidgetItem(f"Step {i+1}"))
            self.table.setItem(i, 1, QTableWidgetItem(f"Value {i+1}"))
            self.table.setItem(i, 2, QTableWidgetItem("2"))  # Default duration of 2 seconds

        self.table.selectRow(0)  # Select the first row by default

        # Buttons
        self.prev_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")
        self.run_button = QPushButton("Run/Pause")
        self.prev_button.clicked.connect(self.previous_row)
        self.next_button.clicked.connect(self.next_row)
        self.run_button.clicked.connect(self.toggle_run_pause)

        # Adding widgets to layouts
        self.button_layout.addWidget(self.prev_button)
        self.button_layout.addWidget(self.next_button)
        self.button_layout.addWidget(self.run_button)
        self.layout.addLayout(self.button_layout)
        self.layout.addWidget(self.table)

        # Set the main layout
        self.setLayout(self.layout)

        # Timer setup
        self.timer.timeout.connect(self.process_row)

    def previous_row(self):
        current_row = self.table.currentRow()
        if current_row > 0:
            self.table.selectRow(current_row - 1)

    def next_row(self):
        current_row = self.table.currentRow()
        if current_row < self.table.rowCount() - 1:
            self.table.selectRow(current_row + 1)

    def toggle_run_pause(self):
        if self.is_running:
            self.timer.stop()
            self.run_button.setText("Run")
        else:
            if self.table.currentRow() == self.table.rowCount() - 1:
                self.table.selectRow(0)  # Restart from the beginning if at the end
            self.timer.start(int(self.table.item(self.table.currentRow(), 2).text()) * 1000)
            self.run_button.setText("Pause")
        self.is_running = not self.is_running

    def process_row(self):
        self.current_row = self.table.currentRow()
        description = self.table.item(self.current_row, 0).text()
        value = self.table.item(self.current_row, 1).text()
        print(f"Running {description} with value {value}")

        if self.current_row < self.table.rowCount() - 1:
            self.table.selectRow(self.current_row + 1)
            duration = int(self.table.item(self.table.currentRow(), 2).text()) * 1000
            self.timer.start(duration)
        else:
            self.timer.stop()
            self.run_button.setText("Run")
            self.is_running = False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller = TableController()
    controller.show()
    sys.exit(app.exec())
