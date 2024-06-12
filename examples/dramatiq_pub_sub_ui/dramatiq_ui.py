import json
import dramatiq
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget, QMessageBox, QPushButton
from PySide6.QtCore import Signal
from examples.dramatiq_pub_sub_ui.dramatiq_publisher import publish_message


class MainWindow(QWidget):
    show_popup_signal = Signal(str)
    def __init__(self):
        super().__init__()

        self.label = QLabel("Waiting for messages...")
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.publish_button = QPushButton("Publish message")
        self.publish_button.clicked.connect(self.publish_button_clicked)
        layout.addWidget(self.publish_button)
        self.show_popup_signal.connect(self.show_popup)

    def show_popup(self, message):
        self.label.setText(f"Received message: {message}")
        msg_box = QMessageBox()
        msg_box.setText(f"Received message: {message}")
        msg_box.exec()

    @staticmethod
    def publish_button_clicked():
        print("Publishing message")
        topic = "ui.event.publish_button.clicked"
        message = "Hello world!"
        publish_message(message, topic, actor_to_send="orchestrator_actor")


class MainWindowController:
    def __init__(self, window):
        self.window = window
        self.on_publish_button_clicked_actor = MainWindow.publish_button_clicked

        @dramatiq.actor
        def ui_listener_actor(message, topic):

            if "popup" in topic:
                self.window.show_popup_signal.emit(message)


