import functools

import dramatiq
import dropbot
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget, QMessageBox, QPushButton
from PySide6.QtCore import Signal
from apscheduler.events import EVENT_JOB_EXECUTED
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from examples.dropbot_pub_sub.dropbot_searcher import check_dropbot_devices_available
from microdrop_utils._logger import get_logger
from microdrop_utils.pub_sub_serial_proxy import DropbotSerialProxy

logger = get_logger(__name__)


class MainWindow(QWidget):
    show_popup_signal = Signal(str)

    def __init__(self):
        super().__init__()

        self.label = QLabel("Waiting for messages...")
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.connect_button = QPushButton("Connect to DropBot")
        layout.addWidget(self.connect_button)
        self.show_popup_signal.connect(self.show_popup)

    def show_popup(self, message):
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

        self.proxy: DropbotSerialProxy = None
        self.port_name = None

        scheduler = BackgroundScheduler()

        self.dropbot_search_submitted = False
        # Add a job to the scheduler with the specific argument
        hwids_to_check = ["VID:PID=16C0:"]  # the teensy id (the dropbot device)
        scheduler.add_job(
            func=functools.partial(check_dropbot_devices_available, hwids_to_check),
            trigger=IntervalTrigger(seconds=1),
        )

        # Add listeners to handle job events
        scheduler.add_listener(self.on_dropbot_port_found, EVENT_JOB_EXECUTED)

        self.scheduler = scheduler

        self.ui_listener = self.create_ui_listener_actor()
        self.make_serial_proxy = self._make_serial_proxy()

        self.actor_topics_dict = {"ui_listener_actor": ["dropbot/signals/+"]}

    def connect_button_clicked(self):
        """
        Handle the connect button click event.
        """
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("DropBot detection job started.")

        elif self.proxy:
            self.window.show_popup_signal.emit("DropBot already connected.")
            logger.info("DropBot already connected.")

        else:
            logger.info("DropBot detection job already submitted.")

    def on_dropbot_port_found(self, event):
        # pause looking for DropBot devices
        self.scheduler.pause()
        # get port name
        port_name = str(event.retval)
        # send actor job to connect to DropBot
        self.make_serial_proxy.send(port_name)

    def _make_serial_proxy(self):

        @dramatiq.actor
        def make_serial_proxy(port_name):
            try:
                self.proxy = DropbotSerialProxy(port=port_name)
                logger.info(f"Connected to DropBot on port {port_name}")

            except (IOError, AttributeError):
                self.window.show_popup_signal.emit('No DropBot available for connection')
                logger.error("No DropBot available for connection")

            except dropbot.proxy.NoPower:
                self.window.show_popup_signal.emit('No power to DropBot')
                logger.error("No power to DropBot")

            self.setup_dropbot()

        return make_serial_proxy

    def setup_dropbot(self):
        """
        Setup the DropBot serial proxy.
        """
        OUTPUT_ENABLE_PIN = 22
        # Chip may have been inserted before connecting, so `chip-inserted`
        # event may have been missed.
        # Explicitly check if chip is inserted by reading **active low**
        # `OUTPUT_ENABLE_PIN`.
        if self.proxy.digital_read(OUTPUT_ENABLE_PIN):
            self.window.show_popup_signal.emit("Chip not inserted")
        else:
            self.window.show_popup_signal.emit("Chip inserted")

        self.proxy.signals.signal('output_enabled').connect(self.output_state_changed_wrapper)
        self.proxy.signals.signal('output_disabled').connect(self.output_state_changed_wrapper)

    def output_state_changed_wrapper(self, signal: dict[str, str]):
        if signal['event'] == 'output_enabled':
            self.window.show_popup_signal.emit("Chip inserted")
        elif signal['event'] == 'output_disabled':
            self.window.show_popup_signal.emit("Chip not inserted")
        else:
            logger.warn(f"Unknown signal received: {Signal}")

    def create_ui_listener_actor(self):
        """
        Create a Dramatiq actor for listening to UI-related messages.

        Returns:
        dramatiq.Actor: The created Dramatiq actor.
        """

        @dramatiq.actor
        def ui_listener_actor(message, topic):
            """
            A Dramatiq actor that listens to UI-related messages.

            Parameters:
            message (str): The received message.
            topic (str): The topic of the message.
            """
            logger.info(f"UI_LISTENER: Received message: {message} from topic: {topic}")

            topic = topic.split("/")

            if topic[-1] == "connected":
                self.window.show_popup_signal.emit("DropBot connected")

            if topic[-1] == "disconnected":
                self.window.show_popup_signal.emit("DropBot disconnected")
                self.proxy.terminate()
                del self.proxy
                del self.port_name

            if "popup" in topic:
                self.window.show_popup_signal.emit(message)

        return ui_listener_actor
