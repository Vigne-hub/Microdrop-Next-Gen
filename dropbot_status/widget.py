# sys imports
import json
import os

# pyside imports
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout, QPushButton, QMessageBox, QHBoxLayout, QDialog, QTextBrowser
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap

# local imports
from microdrop_utils._logger import get_logger
from microdrop_utils.base_dropbot_qwidget import BaseDramatiqControllableDropBotQWidget
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
        self.setFixedSize(250, 100)

        self.status_bar = QHBoxLayout()

        self.dropbot_icon = QLabel()
        self.dropbot_icon.setFixedSize(100, 100)
        self.status_bar.addWidget(self.dropbot_icon)

        self.text_layout = QVBoxLayout()

        # Default status to disconnected
        self.dropbot_connection_status = QLabel()
        self.dropbot_chip_status = QLabel()
        self.update_status_icon(dropbot_connected=False, chip_inserted=False)

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
            logger.info("Dropbot Connected")
            self.dropbot_connection_status.setText("Connected")

            if chip_inserted:
                logger.info("Chip Inserted")
                # dropbot ready to use: give greenlight and display chip.
                self.dropbot_chip_status.setText("Chip inserted")
                img_path = DROPBOT_CHIP_INSERTED_IMAGE
                status_color = green

            # dropbot connected but no chip inside. Yellow signal.
            else:
                logger.info("Chip Not Inserted")
                self.dropbot_chip_status.setText("Chip not inserted")
                img_path = DROPBOT_IMAGE
                status_color = yellow

        else:
            # dropbot not there. Red light.
            logger.info("Dropbot Disconnected")
            img_path = DROPBOT_IMAGE
            status_color = red
            self.dropbot_connection_status.setText("Disconnected")
            self.dropbot_chip_status.setText("Chip not inserted")

        pixmap = QPixmap(img_path)
        if pixmap.isNull():
            logger.error(f"Failed to load image: {img_path}")

        self.dropbot_icon.setPixmap(pixmap.scaled(100, 150, Qt.AspectRatioMode.KeepAspectRatio))
        self.dropbot_icon.setStyleSheet('QLabel { background-color : %s ; }' % status_color)

    def update_capacitance_reading(self, capacitance):
        self.dropbot_capacitance_reading.setText(f"Capacitance: {capacitance}")

    def update_voltage_reading(self, voltage):
        self.dropbot_voltage_reading.setText(f"Voltage: {voltage}")


class DropBotStatusWidget(BaseDramatiqControllableDropBotQWidget):
    def __init__(self):
        super().__init__()

        # flag for if no pwoer is true or not
        self.no_power_dialog = None
        self.no_power = None
        self.layout = QVBoxLayout(self)

        self.status_label = DropBotStatusLabel()
        self.layout.addWidget(self.status_label)

    ###################################################################################################################
    # Publisher methods
    ###################################################################################################################
    def request_detect_shorts(self):
        logger.info("Detecting shorts...")
        publish_message("Detect shorts button triggered", DETECT_SHORTS)

    def request_retry_connection(self):
        logger.info("Retrying connection...")
        publish_message("Retry connection button triggered", RETRY_CONNECTION)

        if self.no_power_dialog:
            self.no_power_dialog.close()

        self.no_power = False
        self.no_power_dialog = None

    ###################################################################################################################
    # Subscriber methods
    ###################################################################################################################

    ######################################### Handler methods #############################################

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
        capacitance = json.loads(body).get('capacitance', '0 pF')
        voltage = json.loads(body).get('voltage', '0 V')
        self.status_label.update_capacitance_reading(capacitance)
        self.status_label.update_voltage_reading(voltage)

    ####### Dropbot Icon Image Control Methods ###########

    def _on_disconnected_triggered(self, body):
        self.status_label.update_status_icon(dropbot_connected=False, chip_inserted=False)

    def _on_chip_not_inserted_triggered(self, body):
        self.status_label.update_status_icon(dropbot_connected=True, chip_inserted=False)

    def _on_chip_inserted_triggered(self, body):
        self.status_label.update_status_icon(dropbot_connected=True, chip_inserted=True)

    ##################################################################################################

    ########## Warning methods ################
    def _on_show_warning_triggered(self, body): # This is not controlled by the dramatiq controller! Called manually in dramatiq_dropbot_status_controller.py
        body = json.loads(body)

        title = body.get('title', ''),
        message = body.get('message', '')

        self.warning_popup = QMessageBox()
        self.warning_popup.setWindowTitle(f"WARNING: {title}")
        self.warning_popup.setText(str(message))
        self.warning_popup.exec()

    def _on_no_power_triggered(self, body):
        if self.no_power:
            return

        self.no_power = True
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
        self.no_power_retry_button.clicked.connect(self.request_retry_connection)

        # Add widgets to the layout
        layout.addWidget(self.browser)
        layout.addWidget(self.no_power_retry_button)

        # Show the dialog
        self.no_power_dialog.exec()

    def _on_halted_triggered(self, message):
        self.halted_popup = QMessageBox()
        self.halted_popup.setWindowTitle("ERROR: DropBot Halted")
        self.halted_popup.setButtonText(QMessageBox.StandardButton.Ok, "Close")
        self.halted_popup.setText(f"DropBot has been halted, reason was {message}."
                                  "\n\n"
                                  "All channels have been disabled and high voltage has been turned off until "
                                  "the DropBot is restarted (e.g. unplug all cables and plug back in).")

        self.halted_popup.exec()

