from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QPushButton, QHeaderView)


class ProtocolGridController(QWidget):
    """
    A modular Protocol Grid Controller that can be imported and used in other files.
    It can interact with signals from a Dropbot controlling widget.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        self.protocolTable = QTableWidget()
        self.protocolTable.setColumnCount(4)  # You can adjust the number of columns based on your requirements
        self.protocolTable.setHorizontalHeaderLabels(['Step', 'Duration', 'Voltage', 'Electrodes'])
        self.protocolTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.protocolTable)

        self.addRowButton = QPushButton('Add Row')
        self.addRowButton.clicked.connect(self.add_row)
        self.layout.addWidget(self.addRowButton)

    def add_row(self):
        row_position = self.protocolTable.rowCount()
        self.protocolTable.insertRow(row_position)

    def collect_protocol_data(self):
        """
        Collect data from the protocol table and return it.
        You'll need to define the structure of this data based on how you plan to use it.
        """
        data = []
        for row in range(self.protocolTable.rowCount()):
            row_data = {}
            for column in range(self.protocolTable.columnCount()):
                item = self.protocolTable.item(row, column)
                if item is not None:  # Check if the item exists
                    row_data[self.protocolTable.horizontalHeaderItem(column).text()] = item.text()
                else:
                    row_data[self.protocolTable.horizontalHeaderItem(column).text()] = ""
            data.append(row_data)
        return data


# Test code
if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    protocol_grid = ProtocolGridController()
    protocol_grid.show()
    sys.exit(app.exec())
