import json
import os
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton, QMessageBox, QHBoxLayout, QDialog
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
        self.status_bar.addWidget(self.dropbot_icon)

        self.text_layout = QVBoxLayout()
        self.dropbot_connection_status = QLabel("Disconnected")
        self.dropbot_chip_status = QLabel("No chip inserted")
        self.dropbot_capacitance_reading = QLabel("Capacitance: 0 pF")
        self.dropbot_voltage_reading = QLabel("Voltage: 0 V")

        self.text_layout.addWidget(self.dropbot_connection_status)
        self.text_layout.addWidget(self.dropbot_chip_status)
        self.text_layout.addWidget(self.dropbot_capacitance_reading)
        self.text_layout.addWidget(self.dropbot_voltage_reading)

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
        self.dropbot_capacitance_reading.setText(f"Capacitance: {capacitance} F")

    def update_voltage_reading(self, voltage):
        self.dropbot_voltage_reading.setText(f"Voltage: {voltage} V")


class DropBotControlWidget(QWidget):
    signal_received = Signal(str)

    def __init__(self):
        super().__init__()
        # Subscribe to backend messages
        self.actor_topics_dict = {"dropbot_status_listener": ["dropbot/signals/#"]}

        # create listener actor:
        self.dropbot_status_listener = self.create_dropbot_status_listener_actor()

        self.layout = QVBoxLayout(self)

        self.status_label = DropBotStatusLabel()
        self.layout.addWidget(self.status_label)

        self.detect_shorts_button = QPushButton("Detect Shorts")
        self.detect_shorts_button.clicked.connect(self.detect_shorts_triggered)
        self.layout.addWidget(self.detect_shorts_button)

        self.signal_received.connect(self.signal_handler)

        self.setup_halted_popup()

    def setup_halted_popup(self):
        self.halted_popup_layout = QVBoxLayout()

        self.halted_popup = QMessageBox()
        self.halted_popup.setText("Please Unplug USB and Power Cables and Plug the Power then the USB Cable Back In")

        self.halted_image = QLabel()
        self.halted_popup_layout.addWidget(self.halted_image)

        self.button = QPushButton('Next')
        self.button.clicked.connect(self.next_image)
        self.halted_popup_layout.addWidget(self.button)

        # Automatically find all images in the images directory
        self.image_dir = os.path.join(os.path.dirname(__file__), "images")
        self.images = [os.path.join(self.image_dir, f) for f in os.listdir(self.image_dir) if f.endswith('.png') and 'power' in f]
        self.current_image = 0

        # Load the first image
        self.update_image()
        self.halted_popup.setLayout(self.halted_popup_layout)

    def update_image(self):
        pixmap = QPixmap(self.images[self.current_image])
        self.halted_image.setPixmap(pixmap.scaled(320, 320, Qt.AspectRatioMode.KeepAspectRatio))

    def next_image(self):
        if self.current_image < len(self.images) - 1:
            self.current_image += 1
            self.update_image()
            if self.current_image == len(self.images) - 1:
                self.button.setText('Exit')
        else:
            self.halted_popup.close()

    def show_halted_popup(self):
        self.halted_popup.exec()

    def show_shorts_popup(self, shorts):
        self.shorts_popup_layout = QVBoxLayout()
        self.shorts_popup = QMessageBox()
        self.shorts_popup.setFixedSize(300, 200)
        self.shorts_popup.setWindowTitle("Shorts Detected")
        self.shorts_popup.setLayout(self.shorts_popup_layout)
        if len(shorts) > 0:
            shorts_str = str(shorts).strip('[]')
            self.shorts_popup.setText(f"Electrodes: {shorts_str}")
        else:
            self.shorts_popup.setText("None")

        self.shorts_popup.exec()

    def detect_shorts_triggered(self):
        logger.info("Detecting shorts...")
        publish_message("Detect shorts button triggered", "dropbot/ui/notifications/detect_shorts_triggered")

    def detect_shorts_response(self, shorts_dict):
        shorts_list = json.loads(shorts_dict).get('Shorts_detected', [])
        self.show_shorts_popup(shorts_list)

    def show_warning(self, title, message):
        self.warning_popup = QMessageBox()
        self.warning_popup.setWindowTitle(title)
        self.warning_popup.setText(message)
        self.warning_popup.exec()

    def signal_handler(self, message):
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
        elif "halted" in topic:
            self.show_halted_popup()
        elif "capacitance_updated" in topic:
            capacitance = json.loads(body).get('capacitance', 0)
            voltage = json.loads(body).get('voltage', 0)
            self.status_label.update_capacitance_reading(capacitance)
            self.status_label.update_voltage_reading(voltage)

    def create_dropbot_status_listener_actor(self):

        @dramatiq.actor
        def dropbot_status_listener(message, topic):
            logger.info(f"UI_LISTENER: Received message: {message} from topic: {topic}")
            topic_elements = topic.split("/")
            if topic_elements[-1] in ['connected', 'disconnected', 'chip_inserted', 'chip_not_inserted', 'no_power',
                                      'no_dropbot_available', 'shorts_detected', 'halted', 'capacitance_updated']:

                self.signal_received.emit(f"{topic}, {message}")

        return dropbot_status_listener


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dropbot_status = DropBotControlWidget()
    dropbot_status.show()
    sys.exit(app.exec())
