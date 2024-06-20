import dramatiq
import dropbot
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget, QMessageBox, QPushButton
from PySide6.QtCore import Signal
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from examples.dropbot_pub_sub.dropbot_searcher import DropbotSearcher
from microdrop_utils.dramatiq_pub_sub_helpers import publish_message

from microdrop_utils._logger import get_logger
from microdrop_utils.pub_sub_serial_proxy import DropbotSerialProxy

logger = get_logger(__name__)


class MainWindow(QWidget):
    output_state_changed = Signal(bool)
    show_dropbot_connection_popup_signal = Signal(str)

    def __init__(self):
        super().__init__()

        self.label = QLabel("Waiting for messages...")
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.connect_button = QPushButton("Connect to DropBot")
        layout.addWidget(self.connect_button)
        self.output_state_changed.connect(self.output_state_changed_handler)
        self.show_dropbot_connection_popup_signal.connect(self.show_dropbot_connection_popup)

    def output_state_changed_handler(self, state):
        self.label.setText(f"Output state changed: {state}")
        msg_box = QMessageBox()
        msg_box.setText(f"Output state changed: {state}")
        msg_box.exec()

    def show_dropbot_connection_popup(self, message):
        self.label.setText(f"Received message: {message}")
        msg_box = QMessageBox()
        msg_box.setText(f"Received message: {message}")
        msg_box.exec()


class MainWindowController:
    """
    Controller class for handling the main window logic.
    """

    def __init__(self, window):
        """
        Initialize the MainWindowController with the given window.

        Parameters:
        window (QMainWindow): The main window instance.
        """
        self.window = window
        self.window.connect_button.clicked.connect(self.connect_button_clicked)
        self.make_dropbot_proxy_actor = self._make_serial_proxy()
        self.dropbot_connection_monitor = self.create_connection_monitor()
        self.proxy: DropbotSerialProxy = None

        example_instance = DropbotSearcher()
        scheduler = BackgroundScheduler()
        scheduler.add_job(example_instance.check_dropbot_devices_available_actor.send, 'interval', seconds=2)
        self.scheduler = scheduler

    def connect_button_clicked(self):
        """
        Handle the connect button click event.
        """
        if not self.scheduler.running:
            self.scheduler.start()
        else:
            logger.info("DropBot connection already being monitored.")

    def _make_serial_proxy(self):
        @dramatiq.actor
        def make_serial_proxy(port_names, topic):
            self.scheduler.shutdown()
            example_instance = DropbotSearcher()
            scheduler = BackgroundScheduler()
            scheduler.add_job(example_instance.check_dropbot_devices_available_actor.send, 'interval', seconds=2)
            self.scheduler = scheduler

            try:
                self.proxy = DropbotSerialProxy(port=port_names[0])
            except (IOError, AttributeError):
                self.window.show_dropbot_connection_popup_signal.emit('No DropBot available for connection')

            except dropbot.proxy.NoPower:
                self.window.show_dropbot_connection_popup_signal.emit('No power to DropBot')

            self.setup_dropbot()

        return make_serial_proxy

    def setup_dropbot(self):
        """
        Setup the DropBot serial proxy.
        """
        self.proxy.signals.signal('output_enabled').connect(self.output_state_changed_wrapper)
        self.proxy.signals.signal('output_disabled').connect(self.output_state_changed_wrapper)

        OUTPUT_ENABLE_PIN = 22
        # Chip may have been inserted before connecting, so `chip-inserted`
        # event may have been missed.
        # Explicitly check if chip is inserted by reading **active low**
        # `OUTPUT_ENABLE_PIN`.
        if self.proxy.digital_read(OUTPUT_ENABLE_PIN):
            self.window.output_state_changed.emit(False)
        else:
            self.window.output_state_changed.emit(True)

    def output_state_changed_wrapper(self, signal: dict[str, str]):
        if signal['event'] == 'output_enabled':
            self.window.output_state_changed.emit(True)
        elif signal['event'] == 'output_disabled':
            self.window.output_state_changed.emit(False)
        else:
            print("Unknown signal received: %s", signal)

    def create_connection_monitor(self):
        """
        Create a Dramatiq actor for listening to UI-related messages.

        Returns:
        dramatiq.Actor: The created Dramatiq actor.
        """

        @dramatiq.actor
        def dropbot_connection_monitor(message, topic):
            """
            A Dramatiq actor that listens to UI-related messages.

            Parameters:
            message (str): The received message.
            topic (str): The topic of the message.
            """
            logger.info(f"UI_LISTENER: Received message: {message} from topic: {topic}")

            if "disconnect" in topic:
                if self.scheduler.running:
                    self.scheduler.shutdown()
                self.proxy.terminate()

            self.window.show_dropbot_connection_popup_signal.emit(message)

        return dropbot_connection_monitor
