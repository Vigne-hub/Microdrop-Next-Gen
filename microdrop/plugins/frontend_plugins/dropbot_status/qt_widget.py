import json
import os
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton, QMessageBox, QHBoxLayout
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QPixmap
import sys
import dramatiq
from microdrop_utils._logger import get_logger
from microdrop_utils.dramatiq_pub_sub_helpers import publish_message

logger = get_logger(__name__)


class DropBotStatusLabel(QLabel):
    red = '#f15854'
    yellow = '#decf3f'
    green = '#60bd68'
    status_color = None

    def __init__(self):
        super().__init__()
        self.setFixedSize(500, 100)
        self.status_bar = QHBoxLayout()
        self.dropbot_icon = QLabel()
        self.dropbot_icon.setFixedSize(100, 100)
        self.text_layout = QVBoxLayout()
        self.dropbot_connection_status = QLabel("Disconnected")
        self.dropbot_chip_status = QLabel("No chip inserted")
        self.dropbot_capacitance_reading = QLabel("Capacitance: 0 pF")
        self.shorts_label = QLabel("Shorts: None")

        self.status_bar.addWidget(self.dropbot_icon)
        self.text_layout.addWidget(self.dropbot_connection_status)
        self.text_layout.addWidget(self.dropbot_chip_status)
        self.text_layout.addWidget(self.dropbot_capacitance_reading)
        self.text_layout.addWidget(self.shorts_label)
        self.status_bar.addLayout(self.text_layout)
        self.setLayout(self.status_bar)

        self.update_status_icon('disconnected', self.red)  # Default to disconnected

    def update_status_icon(self, status, status_color):
        images = {
            'connected': 'dropbot-chip-inserted.png',
            'disconnected': 'dropbot.png',
            'chip_inserted': 'dropbot-chip-inserted.png',
            'chip_removed': 'dropbot.png',
            'no_power': 'dropbot.png',
            'no_dropbot_available': 'dropbot.png'
        }

        current_file_path = __file__
        current_folder_path = os.path.dirname(os.path.abspath(current_file_path))
        img_path = os.path.join(current_folder_path, 'images', images[status])

        pixmap = QPixmap(img_path)
        if pixmap.isNull():
            logger.error(f"Failed to load image: {img_path}")

        self.dropbot_icon.setPixmap(pixmap.scaled(100, 150, Qt.AspectRatioMode.KeepAspectRatio))
        self.dropbot_icon.setStyleSheet('QLabel { background-color : %s ; }' % status_color)

    def update_connection_status(self, connection_status):
        logger.info(f"Attempting to update connection status: {connection_status}")
        if connection_status == 'connected':
            self.update_status_icon('connected', self.green)
        elif connection_status == 'disconnected':
            self.update_status_icon('disconnected', self.red)
        self.dropbot_connection_status.setText(connection_status.capitalize())

    def update_chip_status(self, chip_status):
        if chip_status == 'chip_inserted':
            self.update_status_icon('chip_inserted', self.green)
        elif chip_status == 'chip_removed':
            self.update_status_icon('chip_removed', self.yellow)
        self.dropbot_chip_status.setText(chip_status.capitalize())

    def update_capacitance_reading(self, capacitance):
        self.dropbot_capacitance_reading.setText(f"Capacitance: {capacitance} pF")

    def update_shorts(self, shorts):
        if len(shorts) > 0:
            shorts_str = str(shorts).strip('[]')
            self.shorts_label.setText(f"Shorts: {shorts_str}")
        else:
            self.shorts_label.setText("Shorts: None")


class DropBotControlWidget(QWidget):
    signal_received = Signal(str)
    device_connected = False

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.status_label = DropBotStatusLabel()
        self.layout.addWidget(self.status_label)

        self.detect_shorts_button = QPushButton("Detect Shorts")
        self.detect_shorts_button.clicked.connect(self.detect_shorts_triggered)
        self.layout.addWidget(self.detect_shorts_button)

        self.signal_received.connect(self.handle_signal)

        # Subscribe to backend messages
        self.actor_topics_dict = {"dropbot_status_listener": ["dropbot/ui/#"]}

        # create actors:
        self.dropbot_status_listener = self.create_dropbot_status_listener_actor()

    def detect_shorts_triggered(self):
        logger.info("Detecting shorts...")
        publish_message("Detect shorts button triggered", "dropbot/ui/notifications/detect_shorts_triggered")

    def detect_shorts_response(self, shorts_dict):
        print(shorts_dict)
        shorts_list = json.loads(shorts_dict).get('Shorts_detected', [])
        logger.info(f"Shorts detected received by GUI: {shorts_list}")
        self.status_label.update_shorts(shorts_list)

    def show_warning(self, title, message):
        QMessageBox.information(self, title, message)

    def handle_signal(self, message):
        topic, body = message.split(", ", 1)
        if "disconnected" in topic:
            self.status_label.update_connection_status('disconnected')
        elif "connected" in topic:
            self.status_label.update_connection_status('connected')
        elif "chip_inserted" in topic:
            self.status_label.update_chip_status('chip_inserted')
        elif "chip_not_inserted" in topic:
            self.status_label.update_chip_status('chip_removed')
        elif "no_power" in topic:
            self.show_warning('WARNING: no_power', f'{body}')
        elif "no_dropbot_available" in topic:
            self.show_warning('WARNING: no_dropbot_available', f'{body}')
        elif "shorts_detected" in topic:
            self.detect_shorts_response(body)

    def create_dropbot_status_listener_actor(self):

        @dramatiq.actor
        def dropbot_status_listener(message, topic):
            logger.info(f"UI_LISTENER: Received message: {message} from topic: {topic}")
            topic_elements = topic.split("/")
            if topic_elements[-1] in ['connected', 'disconnected', 'chip_inserted', 'chip_not_inserted', 'no_power',
                                      'no_dropbot_available', 'shorts_detected']:
                self.signal_received.emit(f"{topic}, {message}")

        return dropbot_status_listener


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dropbot_status = DropBotControlWidget()
    dropbot_status.show()
    sys.exit(app.exec())
