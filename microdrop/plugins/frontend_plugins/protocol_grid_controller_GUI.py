import json
import os

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QTableWidget, QHeaderView,
                               QSizePolicy, QStyle, QGroupBox, QLabel, QSpinBox, QTableWidgetItem, QCheckBox,
                               QFileDialog)
from envisage.plugin import Plugin
from traits.trait_types import List


class ProtocolGridController(QWidget):

    def __init__(self, event_hub_plugin, pub_sub_manager, parent=None):
        super().__init__(parent=parent)

        self.event_hub_plugin = event_hub_plugin
        self.pub_sub_manager = pub_sub_manager

        self.is_running = False
        # Initialize members of the class
        self.hbox_control_flow = None
        self.layout = QVBoxLayout(self)
        self.protocol_table_box = QGroupBox("Protocol Grid")
        self.protocol_layout = QVBoxLayout()
        self.protocol_table = QTableWidget(0, 4)  # Step, Description, Duration (s)
        self.timer = QTimer()
        self.current_repetition = 1
        self.remaining_time_update_timer = QTimer()
        self.remaining_time_update_timer.setInterval(1000)

        self.create_table_publisher()

        self.add_experiment_buttons()
        self.setup_protocol_labels()
        self.setup_table()
        self.setup_buttons()

        self.protocol_table.selectionModel().selectionChanged.connect(self.on_selection_changed)
        self.protocol_table.cellChanged.connect(self.on_cell_changed)
        self.sub_to_electrode_clicked_queue()
        self.create_publisher_for_electrode_click()


    def create_table_publisher(self):
        self.pub_sub_manager.create_publisher("protocol_grid_view_publisher", "protocol_grid_view_changed")

    def add_experiment_buttons(self):
        self.hbox_exp_buttons = QHBoxLayout()
        self.hbox_exp_buttons.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.hbox_exp_buttons.setSpacing(10)
        self.hbox_exp_buttons.setContentsMargins(10, 0, 10, 0)

        self.open_experiment_log = QPushButton("Open...")
        self.open_experiment_log.setFixedSize(100, 30)
        self.open_experiment_log.clicked.connect(self.load_protocol)

        self.notes_button = QPushButton("Notes...")
        self.notes_button.setFixedSize(100, 30)

        self.hbox_exp_buttons.addWidget(self.open_experiment_log)
        self.hbox_exp_buttons.addWidget(self.notes_button)

        self.layout.addLayout(self.hbox_exp_buttons)

    def setup_protocol_labels(self):
        self.realtime_checkbox = QCheckBox("Realtime")
        self.realtime_checkbox.setChecked(True)
        self.layout.addWidget(self.realtime_checkbox)

        self.protocol_label_layout = QVBoxLayout()
        self.protocol_label_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.protocol_label_layout.setSpacing(5)
        self.protocol_label_layout.setContentsMargins(0, 0, 10, 0)

        self.protocol_label_hbox1 = QHBoxLayout()
        self.protocol_label_hbox1.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.protocol_label_hbox1.setSpacing(0)
        self.protocol_label_hbox1.setContentsMargins(0, 0, 0, 0)

        self.repeat_hbox = QHBoxLayout()
        self.repeat_hbox.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.repeat_hbox.setSpacing(0)
        self.repeat_hbox.setContentsMargins(0, 0, 0, 0)

        self.protocol_label_hbox2 = QHBoxLayout()
        self.protocol_label_hbox2.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.protocol_label_hbox2.setSpacing(0)
        self.protocol_label_hbox2.setContentsMargins(0, 0, 0, 0)

        self.step_time = QLabel("Step Time:   -   ")
        self.step_time.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.protocol_label_hbox1.addWidget(self.step_time)

        repeat_steps = QLabel("Repeat Steps: ")
        self.repeat_dial = QSpinBox()
        self.repeat_dial.setRange(1, 100)
        self.repeat_dial.setValue(1)
        self.repeat_dial.setMinimumWidth(80)
        time_label = QLabel("Times")

        self.repeat_hbox.addWidget(repeat_steps)
        self.repeat_hbox.addWidget(self.repeat_dial)
        self.repeat_hbox.addWidget(time_label)

        self.protocol_label_hbox1.addLayout(self.repeat_hbox)

        self.step_number = QLabel("Step: 1/1 Repetitions 1/1")
        self.protocol_label_hbox2.addWidget(self.step_number)

        self.protocol_label_layout.addLayout(self.protocol_label_hbox1)
        self.protocol_label_layout.addLayout(self.protocol_label_hbox2)
        self.layout.addLayout(self.protocol_label_layout)

    def setup_table(self):
        self.protocol_layout = QVBoxLayout()
        self.protocol_table = QTableWidget(0, 4)
        self.protocol_table.setHorizontalHeaderLabels(['Description', 'Duration (s)', 'Voltage (V)', 'Frequency (Hz)'])
        header = self.protocol_table.horizontalHeader()
        for i in range(4):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
            header.resizeSection(i, 100)

        self.protocol_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.protocol_table.setEditTriggers(
            QTableWidget.EditTrigger.DoubleClicked |
            QTableWidget.EditTrigger.EditKeyPressed |
            QTableWidget.EditTrigger.SelectedClicked)

        self.protocol_layout.addWidget(self.protocol_table)

        combined_width = sum(header.sectionSize(i) for i in range(header.count()))
        self.protocol_table.setMinimumWidth(combined_width + 20)

        self.protocol_table_box.setLayout(self.protocol_layout)
        self.layout.addWidget(self.protocol_table_box)

        self.add_step()
        self.protocol_table.selectRow(0)

    def setup_buttons(self):
        self.hbox_control_flow = QHBoxLayout()
        self.hbox_control_flow.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.hbox_control_flow.setContentsMargins(0, 0, 0, 0)

        self.goto_first_button = QPushButton(
            icon=self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSkipBackward))
        self.goto_first_button.setIconSize(self.goto_first_button.sizeHint())
        self.goto_first_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.goto_first_button.clicked.connect(self.goto_first)
        self.hbox_control_flow.addWidget(self.goto_first_button)

        self.previous_step_button = QPushButton(
            icon=self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekBackward))
        self.previous_step_button.setIconSize(self.previous_step_button.sizeHint())
        self.previous_step_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.previous_step_button.clicked.connect(self.previous_step)
        self.hbox_control_flow.addWidget(self.previous_step_button)

        self.run_button = QPushButton(icon=self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.run_button.setIconSize(self.run_button.sizeHint())
        self.run_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.run_button.clicked.connect(self.run_protocol)
        self.hbox_control_flow.addWidget(self.run_button)

        self.next_step_button = QPushButton(
            icon=self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekForward))
        self.next_step_button.setIconSize(self.next_step_button.sizeHint())
        self.next_step_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.next_step_button.clicked.connect(self.next_step)
        self.hbox_control_flow.addWidget(self.next_step_button)

        self.goto_last_button = QPushButton(
            icon=self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSkipForward))
        self.goto_last_button.setIconSize(self.goto_last_button.sizeHint())
        self.goto_last_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.goto_last_button.clicked.connect(self.goto_last)
        self.hbox_control_flow.addWidget(self.goto_last_button)

        self.goto_first_button.setStyleSheet("QPushButton { background-color: white; }")
        self.goto_last_button.setStyleSheet("QPushButton { background-color: white; }")
        self.previous_step_button.setStyleSheet("QPushButton { background-color: white; }")
        self.run_button.setStyleSheet("QPushButton { background-color: white; }")
        self.next_step_button.setStyleSheet("QPushButton { background-color: white; }")

        self.layout.addLayout(self.hbox_control_flow)

    def add_step(self):
        row_count = self.protocol_table.rowCount()
        self.protocol_table.insertRow(row_count)
        self.setRowToZero(row_count)

    def setRowToZero(self, row_number):
        if 0 <= row_number < self.protocol_table.rowCount():
            for col in range(self.protocol_table.columnCount() - 1):
                self.protocol_table.setItem(row_number, col + 1, QTableWidgetItem('0'))

    def goto_first(self):
        self.protocol_table.selectRow(0)

    def previous_step(self):
        current_row = self.protocol_table.currentRow()
        if current_row > 0:
            self.protocol_table.selectRow(current_row - 1)

    def run_protocol(self):
        if self.is_running:
            self.is_running = False
            self.run_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            self.toggle_buttons(True)
        else:
            self.is_running = True
            self.run_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
            self.toggle_buttons(False)

    def toggle_buttons(self, enable: bool):
        self.goto_first_button.setEnabled(enable)
        self.previous_step_button.setEnabled(enable)
        self.next_step_button.setEnabled(enable)
        self.goto_last_button.setEnabled(enable)

    def next_step(self):
        current_row = self.protocol_table.currentRow()
        print(current_row, self.protocol_table.rowCount() - 1)
        if current_row < self.protocol_table.rowCount() - 1:
            self.protocol_table.selectRow(current_row + 1)
        elif current_row == self.protocol_table.rowCount() - 1:
            self.add_step()
            self.protocol_table.selectRow(current_row + 1)

    def goto_last(self):
        self.protocol_table.selectRow(self.protocol_table.rowCount() - 1)

    def load_protocol(self):
        file_path = QFileDialog.getOpenFileName(None, "Open Protocol", f"{os.getcwd()}{os.sep}Protocol_Saves", "JSON Files (*.json)")[0]
        self.emit_task("protocol_grid_structure_interface", "IPGSService", "load_protocol", [file_path], {})

    def save_protocol(self):
        self.emit_task("protocol_grid_structure_interface", "IPGSService", "save_protocol", [self.protocol_table, f"{os.getcwd()}{os.sep}Protocol_Saves"], {})

    def emit_task(self, interface, service, task_name, args, kwargs):
        self.event_hub_plugin.process_task_actor.send({"interface": interface,
                                                       "service": service,
                                                       "task_name": task_name,
                                                       "args": args, "kwargs": kwargs})

    # TESTING METHODS
    def get_fully_selected_rows(self):
        selected_indexes = self.protocol_table.selectedIndexes()
        row_count = self.protocol_table.rowCount()
        column_count = self.protocol_table.columnCount()

        fully_selected_rows = []

        # Create a set for each row to hold its selected columns
        row_selection = {row: set() for row in range(row_count)}

        # Populate the sets with the selected column indexes
        for index in selected_indexes:
            row_selection[index.row()].add(index.column())

        # Check if all columns in a row are selected
        for row, columns in row_selection.items():
            if len(columns) == column_count:
                fully_selected_rows.append(row)

        return fully_selected_rows

    def on_selection_changed(self):
        fully_selected_rows = self.get_fully_selected_rows()
        print("Fully selected rows:", fully_selected_rows)

    def on_cell_changed(self):
        print("on_cell_changed called")
        table_data = []
        for row in range(self.protocol_table.rowCount()):
            row_data = {}
            for col in range(self.protocol_table.columnCount()):
                item = self.protocol_table.item(row, col)
                row_data[self.protocol_table.horizontalHeaderItem(col).text()] = item.text() if item else ""
            table_data.append(row_data)

        json_snapshot = json.dumps(table_data, indent=4)
        self.emit_task("protocol_grid_structure_interface", "IPGSService", "on_cell_changed", [json_snapshot], {})

    def sub_to_electrode_clicked_queue(self):
        self.pub_sub_manager.create_subscriber("electrode_clicked_subscriber_PGC_GUI")
        self.pub_sub_manager.bind_sub_to_pub("electrode_clicked_subscriber_PGC_GUI", "electrode_clicked_queue")
        self.pub_sub_manager.start_consumer("electrode_clicked_subscriber_PGC_GUI", self.on_electrode_clicked)

    def on_electrode_clicked(self, channel, method, properties, body):
        temp_message = body.decode()
        electrode_list = json.loads(temp_message)

        steps_selected = self.get_fully_selected_rows()
        self.emit_task("protocol_grid_structure_interface", "IPGSService", "on_electrode_clicked", [], {"steps": steps_selected, "electrodes": electrode_list})

class PGCGUIPlugin(Plugin):
    id = 'app.protocol_gric_controller'
    name = 'PGC GUI Plugin'
    service_offers = List(contributes_to='envisage.service_offers')

    def start(self):
        super().start()
        self._register_services()
        self._create_gui()

    def _register_services(self):
        event_hub_plugin = self.application.get_plugin('app.event_hub')
        pub_sub_manager = self.application.get_plugin('app.pubsub_manager')
        self._gui = ProtocolGridController(event_hub_plugin, pub_sub_manager)

    def _create_gui(self):
        self._gui.show()
