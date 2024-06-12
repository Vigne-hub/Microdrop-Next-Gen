from functools import partial
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget, QMessageBox
from PySide6.QtCore import Signal
import dramatiq


class MainWindow(QWidget):
    show_popup_signal = Signal(str)
    def __init__(self):
        super().__init__()

        self.label = QLabel("Waiting for messages...")
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.show_popup_signal.connect(self.show_popup)

    def show_popup(self, message):
        self.label.setText(f"Received message: {message}")
        msg_box = QMessageBox()
        msg_box.setText(f"Received message: {message}")
        msg_box.exec()


class Orchestrator:
    """
    This would be what our envisage app is. A central hub. Or the task as far as GUI is concerned.
    Or it could be a seperate event manager plugin.

    Each service would have a property saying what routes it wants to listen to.

    The orchestrator will obtain all the messages published to every route and direct it to the interested services.

    """
    def __init__(self, window):
        @dramatiq.actor
        def orchestrator_actor(routing_info, message):
            print(f"Received message: {message} from route: {routing_info}")
            if routing_info == "ui.notify":
                on_message_recived_actor.send(message)

        # we can get this as a service from the service registry
        @dramatiq.actor
        def on_message_recived_actor(message):
            """
            This would be a method in the Task class.
            """
            window.show_popup_signal.emit(message)

        self.orchestrator_actor = orchestrator_actor
        self.on_message_recived_actor = on_message_recived_actor
