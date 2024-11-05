# sys imports
import json
import os
import dramatiq

# pyside imports
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout, QPushButton, QMessageBox, QHBoxLayout, QDialog, QTextBrowser
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap

# local imports
from microdrop_utils._logger import get_logger
from microdrop_utils.dramatiq_pub_sub_helpers import publish_message

logger = get_logger(__name__)
from dropbot_controller.consts import DETECT_SHORTS, RETRY_CONNECTION

from .consts import DROPBOT_IMAGE, DROPBOT_CHIP_INSERTED_IMAGE

red = '#f15854'
yellow = '#decf3f'
green = '#60bd68'


class DropBotStatusLabel(QLabel):
    """
    Class providing some status visuals for when chip has been inserted or not. Or when dropbot has any errors.
    """

    def __init__(self):
        super().__init__()

        self.status_bar = QHBoxLayout()

        self.dropbot_icon = QLabel()
        self.dropbot_icon.setFixedSize(100, 100)
        self.status_bar.addWidget(self.dropbot_icon)

        self.text_layout = QVBoxLayout()

        # Default status to disconnected
        self.dropbot_connection_status = QLabel("Disconnected")
        self.dropbot_chip_status = QLabel("No chip inserted")
        self.update_status_icon('disconnected', red)

        # report readings
        self.dropbot_capacitance_reading = QLabel("Capacitance: 0")
        self.dropbot_voltage_reading = QLabel("Voltage: 0")

        self.text_layout.addWidget(self.dropbot_connection_status)
        self.text_layout.addWidget(self.dropbot_chip_status)
        self.text_layout.addWidget(self.dropbot_capacitance_reading)
        self.text_layout.addWidget(self.dropbot_voltage_reading)

        self.status_bar.addLayout(self.text_layout)

        self.setLayout(self.status_bar)

    def update_status_icon(self, dropbot_connected, chip_inserted):
        """
        Update status based on if device connected and chip inserted or not.
        """

        if dropbot_connected:

            if chip_inserted:
                # dropbot ready to use: give greenlight and display chip.
                img_path = DROPBOT_CHIP_INSERTED_IMAGE
                status_color = green

            # dropbot connected but no chip inside. Yellow signal.
            else:
                img_path = DROPBOT_IMAGE
                status_color = yellow

        else:
            # dropbot not there. Red light.
            img_path = DROPBOT_IMAGE
            status_color = red

        pixmap = QPixmap(img_path)
        if pixmap.isNull():
            logger.error(f"Failed to load image: {img_path}")

        self.dropbot_icon.setPixmap(pixmap.scaled(100, 150, Qt.AspectRatioMode.KeepAspectRatio))
        self.dropbot_icon.setStyleSheet('QLabel { background-color : %s ; }' % status_color)

    def update_capacitance_reading(self, capacitance):
        self.dropbot_capacitance_reading.setText(f"Capacitance: {capacitance} pF")

    def update_voltage_reading(self, voltage):
        self.dropbot_voltage_reading.setText(f"Voltage: {voltage} V")


class DropBotStatusWidget(QWidget):
    signal_received = Signal(tuple)

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)

        self.status_label = DropBotStatusLabel()
        self.layout.addWidget(self.status_label)

        self.detect_shorts_button = QPushButton("Detect Shorts")
        self.detect_shorts_button.clicked.connect(self.request_detect_shorts)
        self.layout.addWidget(self.detect_shorts_button)
        self.signal_received.connect(self.signal_handler)

    ###################################################################################################################
    # Publisher methods
    ###################################################################################################################
    def request_detect_shorts(self):
        logger.info("Detecting shorts...")
        publish_message("Detect shorts button triggered", DETECT_SHORTS)

    def request_retry_connection(self):
        logger.info("Retrying connection...")
        publish_message("Retry connection button triggered", RETRY_CONNECTION)
        self.no_power_dialog.close()

    ###################################################################################################################
    # Subscriber methods
    ###################################################################################################################

    def signal_handler(self, signal):
        """
        Handle GUI action required for signal triggered by dropbot status listener.
        """
        topic, body = signal
        head_topic = topic.split('/')[-1]
        sub_topic = topic.split('/')[-2]
        method = f"_on_{head_topic}_triggered"

        if hasattr(self, method) and callable(getattr(self, method)):
            logger.info(f"Method for {head_topic}, {method} getting called.")
            getattr(self, method)(body)

        # special topic warnings. Printed out to screen.
        elif sub_topic == "warnings":
            logger.info(f"Warning triggered. No special method for warning {head_topic}. Generic message produced")

            title = head_topic.replace('_', ' ').title()

            self._on_show_warning_triggered(json.dumps(

                {'title': title,
                 'message': body}
            ))

        else:
            logger.warning(f"Method for {head_topic}, {method} not found.")

    ######################################### Signal handler methods #############################################

    ######## shorts found method ###########
    def _on_shorts_detected_triggered(self, shorts_dict):
        shorts = json.loads(shorts_dict).get('Shorts_detected', [])

        self.shorts_popup = QMessageBox()
        self.shorts_popup.setFixedSize(300, 200)
        self.shorts_popup.setWindowTitle("ERROR: Shorts Detected")
        self.shorts_popup.setButtonText(QMessageBox.StandardButton.Ok, "Close")
        if len(shorts) > 0:
            shorts_str = str(shorts).strip('[]')
            self.shorts_popup.setText(f"Shorts were detected on the following channels: \n \n"
                                      f"[{shorts_str}] \n \n"
                                      f"You may continue using the DropBot, but the affected channels have "
                                      f"been disabled until the DropBot is restarted (e.g. unplug all cabled and plug "
                                      f"back in).")
        else:
            self.shorts_popup.setWindowTitle("Short Detection Complete")
            self.shorts_popup.setText("No shorts were detected.")

        self.shorts_popup.exec()

    ################# Capcitance Voltage readings ##################
    def _on_capacitance_updated_triggered(self, body):
        capacitance = json.loads(body).get('capacitance', 0)
        voltage = json.loads(body).get('voltage', 0)
        self.status_label.update_capacitance_reading(capacitance)
        self.status_label.update_voltage_reading(voltage)

    ####### Dropbot Icon Image Control Methods ###########

    def _on_disconnected_triggered(self, body):
        self.status_label.update_status_icon(dropbot_connected=False, chip_inserted=False)

    def _on_connected_triggered(self, body):
        self.status_label.update_status_icon(dropbot_connected=True, chip_inserted=False)

    def _on_chip_not_inserted_triggered(self, body):
        self.status_label.update_status_icon(dropbot_connected=True, chip_inserted=False)

    def _on_chip_inserted_triggered(self, body):
        self.status_label.update_status_icon(dropbot_connected=True, chip_inserted=True)

    ##################################################################################################

    ########## Warning methods ################
    def _on_show_warning_triggered(self, body):
        body = json.loads(body)

        title = body.get('title', ''),
        message = body.get('message', '')

        self.warning_popup = QMessageBox()
        self.warning_popup.setWindowTitle(f"WARNING: {title}")
        self.warning_popup.setText(str(message))
        self.warning_popup.exec()

    def _on_no_power_triggered(self):
        # Initialize the dialog
        self.no_power_dialog = QDialog()
        self.no_power_dialog.setWindowTitle("ERROR: No Power")
        self.no_power_dialog.setFixedSize(370, 250)

        # Create the layout
        layout = QVBoxLayout()
        self.no_power_dialog.setLayout(layout)

        # Create the web engine view for displaying HTML
        self.browser = QTextBrowser()

        html_content = f"""

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ERROR: No Power</title>
</head>
<body>
    <h3>DropBot currently has no power supply connected.</h3>
    <strong>Plug in power supply cable<br></strong> <img src='{os.path.dirname(__file__)}{os.sep}images{os.sep}dropbot-power.png' width="104" height="90">
    <strong><br>Click the "Retry" button after plugging in the power cable to attempt reconnection</strong>
</body>
</html>

        """

        self.browser.setHtml(html_content)

        # Create the retry button and connect its signal
        self.no_power_retry_button = QPushButton("Retry")
        self.no_power_retry_button.clicked.connect(self.request_retry_connection())

        # Add widgets to the layout
        layout.addWidget(self.browser)
        layout.addWidget(self.no_power_retry_button)

        # Show the dialog
        self.no_power_dialog.exec()

    def _on_halted_triggered(self):
        self.halted_popup = QMessageBox()
        self.halted_popup.setWindowTitle("ERROR: DropBot Halted")
        self.halted_popup.setButtonText(QMessageBox.StandardButton.Ok, "Close")
        self.halted_popup.setText("DropBot has been halted because output current was exceeded."
                                  "\n\n"
                                  "All channels have been disabled and high voltage has been turned off until "
                                  "the DropBot is restarted (e.g. unplug all cables and plug back in)")

        self.halted_popup.exec()

    ##################################################################################################
