from collections import OrderedDict

import dramatiq
# import h5py
from PySide6.QtWidgets import (QApplication, QTreeView, QVBoxLayout, QWidget,
                               QPushButton, QHBoxLayout, QLineEdit, QStyledItemDelegate, QSpinBox, QDoubleSpinBox,
                               QStyle, QSizePolicy)
from PySide6.QtCore import Qt, QEvent, Signal
from PySide6.QtGui import QIntValidator, QDoubleValidator, QStandardItemModel, QStandardItem
from envisage.ids import TASK_EXTENSIONS
from envisage.plugin import Plugin
from traits.trait_types import List
from microdrop_utils._logger import get_logger
from microdrop_utils.dramatiq_pub_sub_helpers import publish_message

logger = get_logger(__name__)


class SpinBoxDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, integer=True):
        super().__init__(parent)
        self.integer = integer

    def createEditor(self, parent, option, index):
        if self.integer:
            editor = QSpinBox(parent)
        else:
            editor = QDoubleSpinBox(parent)
            editor.setDecimals(2)
            editor.setSingleStep(0.01)
        editor.setMinimum(0)
        editor.setMaximum(10000)  # Set as per your requirement
        editor.installEventFilter(self)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.ItemDataRole.EditRole)
        editor.setValue(int(value) if self.integer else float(value))

    def setModelData(self, editor, model, index):
        value = editor.value()
        model.setData(index, value, Qt.ItemDataRole.EditRole)


class PGCItem(QStandardItem):
    def __init__(self, item_type=None, item_data=None):
        super().__init__(item_data)
        self.item_type = item_type
        self.item_data = item_data

    def get_item_type(self):
        return self.item_type

    def get_item_data(self):
        return self.item_data

    def set_item_type(self, item_type):
        self.item_type = item_type

    def set_item_data(self, item_data):
        self.item_data = item_data


class PGCWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pgc_ui_listener = self.create_PGC_UI_listener_actor()
        # self.register_into_messagerouter()
        # create View
        self.tree = QTreeView()
        self.tree.setSelectionMode(QTreeView.SelectionMode.SingleSelection)

        # create Model
        self.model = QStandardItemModel()

        # set Model
        self.tree.setModel(self.model)

        # set Headers for columns
        self.model.setHorizontalHeaderLabels(["Description", "Repetitions", "Duration", "Voltage", "Frequency"])

        self.model.itemChanged.connect(self.send_protocol_from_view)
        self.model.rowsInserted.connect(self.send_protocol_from_view)
        self.model.rowsRemoved.connect(self.send_protocol_from_view)
        self.tree.selectionModel().selectionChanged.connect(self.send_request_to_update_device_view)

        # Set delegates
        repetition_delegate = SpinBoxDelegate(self, integer=True)
        duration_delegate = SpinBoxDelegate(self, integer=False)
        voltage_delegate = SpinBoxDelegate(self, integer=False)
        frequency_delegate = SpinBoxDelegate(self, integer=False)

        self.tree.setItemDelegateForColumn(1, repetition_delegate)
        self.tree.setItemDelegateForColumn(2, duration_delegate)
        self.tree.setItemDelegateForColumn(3, voltage_delegate)
        self.tree.setItemDelegateForColumn(4, frequency_delegate)

        # Set edit trigger to single click
        self.tree.setEditTriggers(QTreeView.EditTrigger.CurrentChanged)

        # Group and Step creation buttons
        self.add_group_button = QPushButton("Add Group")
        self.add_group_button.clicked.connect(lambda: self.add_group(into=False))

        self.add_group_into_button = QPushButton("Add Group Into")
        self.add_group_into_button.clicked.connect(lambda: self.add_group(into=True))

        self.add_step_button = QPushButton("Add Step")
        self.add_step_button.clicked.connect(lambda: self.add_step(into=False))

        self.add_step_into_button = QPushButton("Add Step Into")
        self.add_step_into_button.clicked.connect(lambda: self.add_step(into=True))

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_group_button)
        button_layout.addWidget(self.add_group_into_button)
        button_layout.addWidget(self.add_step_button)
        button_layout.addWidget(self.add_step_into_button)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tree)
        self.layout.addLayout(button_layout)
        self.setLayout(self.layout)

        self.setup_buttons()

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

    def send_request_to_update_device_view(self):
        pass

    def goto_first(self):
        pass

    def previous_step(self):
        pass

    def run_protocol(self):
        pass

    def next_step(self):
        pass

    def goto_last(self):
        pass

    def add_group(self, into=False):
        """
        Add a group to the tree view. If into is True, the group is added as a child of the selected item.
        Otherwise, the group is added as a sibling of the selected item.

        Removes necessity to deselect a direct child of root and setting focus on root to add a group as a
        sibling in the uppermost level.
        """
        # Get the selected items' indices
        selected_indexes = self.tree.selectionModel().selectedIndexes()

        # Set the parent item to the invisible root item
        parent_item = self.model.invisibleRootItem()

        # If there is are multiple selected items, make adjustment based on uppermost selected item
        if selected_indexes:
            selected_index = selected_indexes[0]
            selected_item = self.model.itemFromIndex(selected_index)
            # If Group
            if into and selected_item.get_item_type() == "Description" and selected_item.get_item_data() == "Group":
                parent_item = selected_item
            else:
                parent_item = selected_item.parent() or self.model.invisibleRootItem()

        group_name = PGCItem(item_type="Description", item_data="Group")
        group_rep = PGCItem(item_type="Repetitions", item_data="1")
        group_dur = PGCItem(item_type="Duration", item_data="")
        group_voltage = PGCItem(item_type="Voltage", item_data="")
        group_frequency = PGCItem(item_type="Frequency", item_data="")
        group = [group_name, group_rep, group_dur, group_voltage, group_frequency]
        # make calculate order function
        for group_member in group:
            if group_member.get_item_type() in ["Repetitions", "Description"]:
                group_member.setEditable(True)
            else:
                group_member.setEditable(False)
        parent_item.appendRow(group)
        self.tree.expandAll()

    def add_step(self, into=False):
        selected_indexes = self.tree.selectionModel().selectedIndexes()
        parent_item = self.model.invisibleRootItem()
        if selected_indexes:
            selected_index = selected_indexes[0]
            selected_item = self.model.itemFromIndex(selected_index)
            if into and selected_item.get_item_type() == "Description" and selected_item.get_item_data() == "Group":
                parent_item = selected_item
            else:
                parent_item = selected_item.parent() or self.model.invisibleRootItem()

        step_index = parent_item.rowCount() + 1
        step_name = PGCItem(item_type="Description", item_data=f"Step {step_index}")
        step_rep = PGCItem(item_type="Repetitions", item_data="1")
        step_dur = PGCItem(item_type="Duration", item_data="1.00")
        step_voltage = PGCItem(item_type="Voltage", item_data="0.00")
        step_frequency = PGCItem(item_type="Frequency", item_data="0.00")
        step = [step_name, step_rep, step_dur, step_voltage, step_frequency]

        for step_member in step:
            step_member.setEditable(True)
        parent_item.appendRow(step)
        self.tree.expandAll()

    def clear_view(self):
        self.model.clear()
        self.model.setHorizontalHeaderLabels(["Description", "Repetitions", "Duration", "Voltage", "Frequency"])

    def populate_treeview(self, protocol):
        self.clear_view()

        def add_items(parent, items):
            for key, value in items.items():
                if "Type" in value and value["Type"] == "Group":
                    group_item = PGCItem(item_type="Description", item_data=key)
                    rep_item = PGCItem(item_type="Repetitions", item_data=str(value.get("Repetitions", "")))
                    group_data = [group_item, rep_item, PGCItem(), PGCItem(), PGCItem()]
                    parent.appendRow(group_data)

                    # Add steps within the group
                    add_items(group_item, {k: v for k, v in value.items() if k not in ["Type", "Repetitions"]})
                else:
                    step_data = [
                        PGCItem(item_type="Description", item_data=key),
                        PGCItem(item_type="Repetitions", item_data="1"),
                        PGCItem(item_type="Duration", item_data=f'{value["Duration"]:.2f}'),
                        PGCItem(item_type="Voltage", item_data=f'{value["Voltage"]:.2f}'),
                        PGCItem(item_type="Frequency", item_data=f'{value["Frequency"]:.2f}')
                    ]
                    parent.appendRow(step_data)

        root_item = self.model.invisibleRootItem()
        add_items(root_item, protocol)
        self.tree.expandAll()

    def send_protocol_from_view(self):
        protocol = OrderedDict()

        def process_item(item, parent_protocol):

            description = item.get_item_data()
            item_type = item.get_item_type()

            # Determine if the item is a group or a step
            if item_type == "Group":  # It's a Group
                repetitions = int(item.get_item_data())
                group_name = description
                group_data = OrderedDict(Type="Group", Repetitions=repetitions)

                # Iterate over children (which are steps in this case)
                for i in range(item.rowCount()):
                    child = item.child(i)
                    child_description = child.data()
                    child_data = {
                        "Description": child_description,
                        "Duration": float(child.child(0, 2).data()),
                        "Voltage": float(child.child(0, 3).data()),
                        "Frequency": float(child.child(0, 4).data())
                    }
                    group_data[f"Step {i + 1}"] = child_data

                parent_protocol[group_name] = group_data
            else:  # It's a Step
                parent_protocol[description] = OrderedDict(
                    Description=description,
                    Duration=float(item.child(0, 2).data()),
                    Voltage=float(item.child(0, 3).data()),
                    Frequency=float(item.child(0, 4).data())
                )

        root_item = self.model.invisibleRootItem()
        for i in range(root_item.rowCount()):
            process_item(root_item.child(i), protocol)

        publish_message(message=protocol, topic="pgc_ui/protocol_data/cell_changed")

    def create_PGC_UI_listener_actor(self):
        """
        Create a Dramatiq actor for listening for protocol data messages.

        Returns:
        dramatiq.Actor: The created Dramatiq actor.
        """

        @dramatiq.actor
        def PGC_UI_listener(message, topic):
            """
            A Dramatiq actor that listens to protocol data messages.

            Parameters:
            message (str): The received message.
            topic (str): The topic of the message.
            """
            logger.info(f"PGC UI LISTENER: Received message: {message} from topic: {topic}")

            topic = topic.split("/")

            if topic[-1] == "protocol_data":
                pass

        return PGC_UI_listener
