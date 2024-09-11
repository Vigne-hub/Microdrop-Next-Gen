import json
import os

from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton, QMessageBox, QHBoxLayout, \
    QDialog, QTextBrowser, QLineEdit
from PySide6.QtCore import Qt, Signal, QTimer, QFile, QTextStream, QIODevice, QUrl
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

        # Create a QWebEngineView widget
        self.browser = QWebEngineView()

    def show_halted_popup(self):
        self.halted_popup = QMessageBox()
        self.halted_popup.setWindowTitle("ERROR: DropBot Halted")
        self.halted_popup.setButtonText(QMessageBox.StandardButton.Ok, "Close")
        self.halted_popup.setText("DropBot has been halted because output current was exceeded."
                                  "\n\n"
                                  "All channels have been disabled and high voltage has been turned off until "
                                  "the DropBot is restarted (e.g. unplug all cables and plug back in)")

        self.halted_popup.exec()

    def show_shorts_popup(self, shorts):
        self.shorts_popup = QMessageBox()
        self.shorts_popup.setFixedSize(300, 200)
        self.shorts_popup.setWindowTitle("ERROR: Shorts Detected")
        self.shorts_popup.setButtonText(QMessageBox.StandardButton.Ok, "Close")
        if len(shorts) > 0:
            shorts_str = str(shorts).strip('[]')
            self.shorts_popup.setText(f"Shorts were detected on the following channels: \n \n"
                                      f"[{shorts_str}] \n \n"
                                      f"You may continue using the DropBot, but the affected channels have "
                                      f"been disabled until the DropBot is restarted (e.g. unplug all cabled and plug back in).")
        else:
            self.shorts_popup.setWindowTitle("Short Detection Complete")
            self.shorts_popup.setText("No shorts were detected.")

        self.shorts_popup.exec()

    def show_no_power_popup(self):
        # Initialize the dialog
        self.no_power_dialog = QDialog()
        self.no_power_dialog.setWindowTitle("ERROR: No Power")
        self.no_power_dialog.setFixedSize(370, 250)

        # Create the layout
        layout = QVBoxLayout()
        self.no_power_dialog.setLayout(layout)

        # Create the web engine view for displaying HTML
        self.browser = QWebEngineView()
        html_path = f"{os.path.dirname(__file__)}{os.sep}html_files{os.sep}no_power.html"

        # Load the HTML file into the browser
        self.load_html(html_path)

        # Create the retry button and connect its signal
        self.no_power_retry_button = QPushButton("Retry")
        self.no_power_retry_button.clicked.connect(self.signal_retry_connect)

        # Add widgets to the layout
        layout.addWidget(self.browser)
        layout.addWidget(self.no_power_retry_button)

        # Show the dialog
        self.no_power_dialog.exec()

    def load_html(self, file_path):
        # Open and read the HTML file content
        file = QFile(file_path)
        if file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(file)
            html_content = stream.readAll()

            # Set base URL to the directory of the HTML file
            base_url = QUrl.fromLocalFile(os.path.dirname(file_path) + os.sep)
            self.browser.setHtml(html_content, base_url)

        file.close()

    def detect_shorts_triggered(self):
        logger.info("Detecting shorts...")
        publish_message("Detect shorts button triggered", "dropbot/ui/notifications/detect_shorts_triggered")

    def signal_retry_connect(self):
        logger.info("Retrying connection...")
        publish_message("Retry connection button triggered", "dropbot/ui/notifications/retry_connection_triggered")
        self.no_power_dialog.close()

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
            self.show_no_power_popup()
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

    def create_test_step_command_box(self):
        self.volt_line = QHBoxLayout()
        self.volt_label = QLabel("Voltage: ")
        self.volt_textbox = QLineEdit()
        self.volt_line.addWidget(self.volt_label)
        self.volt_line.addWidget(self.volt_textbox)

        self.freq_line = QHBoxLayout()
        self.freq_label = QLabel("Frequency: ")
        self.freq_textbox = QLineEdit()
        self.freq_line.addWidget(self.freq_label)
        self.freq_line.addWidget(self.freq_textbox)

        self.channels_line = QHBoxLayout()
        self.channels_label = QLabel("Channels: ")
        self.channels_textbox = QLineEdit()
        self.channels_line.addWidget(self.channels_label)
        self.channels_line.addWidget(self.channels_textbox)

        self.layout.addLayout(self.volt_line)
        self.layout.addLayout(self.freq_line)
        self.layout.addLayout(self.channels_line)

        self.test_step_button = QPushButton("Test Step")
        self.test_step_button.clicked.connect(self.test_step_triggered)
        self.layout.addWidget(self.test_step_button)

    def test_step_triggered(self):
        volt = float(self.volt_textbox.text())
        freq = float(self.freq_textbox.text())
        channels = self.channels_textbox.text().replace(' ', '').split(',')

        logger.info(f"Test step triggered with: {volt}, {freq}, {channels}")
        publish_message(json.dumps({"voltage": volt, "frequency": freq, "channels": channels}), "dropbot/ui/notifications/test_step_triggered")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dropbot_status = DropBotControlWidget()
    dropbot_status.show()
    sys.exit(app.exec())
