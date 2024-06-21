from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton, QMessageBox, QHBoxLayout
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
import sys
import pkgutil
import dramatiq
from microdrop_utils._logger import get_logger
from microdrop_utils.dramatiq_pub_sub_helpers import MessageRouterActor

logger = get_logger(__name__)


class DropBotStatusLabel(QLabel):
    red = '#f15854'
    yellow = '#decf3f'
    green = '#60bd68'
    status_color = None

    def __init__(self):
        super().__init__()
        self.setFixedSize(150, 150)

        self.status_bar = QHBoxLayout()
        self.dropbot_icon = QLabel()
        self.text_layout = QVBoxLayout()
        self.dropbot_connection_status = QLabel("Disconnected")
        self.dropbot_chip_status = QLabel("No chip inserted")
        self.dropbot_capacitance_reading = QLabel("Capacitance: 0 pF")

        self.status_bar.addWidget(self.dropbot_icon)
        self.text_layout.addWidget(self.dropbot_connection_status)
        self.text_layout.addWidget(self.dropbot_chip_status)
        self.text_layout.addWidget(self.dropbot_capacitance_reading)
        self.status_bar.addLayout(self.text_layout)
        self.setLayout(self.text_layout)


        self.update_status_icon('disconnected', self.red)  # Default to disconnected


    def update_status_icon(self, status, status_color):
        images = {
            'connected': 'dropbot-chip-inserted.png',
            'disconnected': 'dropbot.png',
            'chip_inserted': 'dropbot-chip-inserted.png',
            'chip_removed': 'dropbot.png',
            'no_power': 'dropbot.png',
            'no_db_available': 'dropbot.png'
        }

        img_blob = pkgutil.get_data(__package__, f'images/{images[status]}')
        pixmap = QPixmap()
        pixmap.loadFromData(img_blob)
        self.dropbot_icon.setPixmap(pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio))
        self.dropbot_icon.setStyleSheet('QLabel { background-color : %s ; }' % status_color)

    def update_connection_status(self, connection_status):
        self.dropbot_connection_status.setText(connection_status.capitalize())

    def update_chip_status(self, chip_status):
        self.dropbot_chip_status.setText(chip_status.capitalize())

    def update_capacitance_reading(self, capacitance):
        self.dropbot_capacitance_reading.setText(f"Capacitance: {capacitance} pF")



class DropBotControlWidget(QWidget):
    signal_received = Signal(str)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        self.status_label = DropBotStatusLabel()
        layout.addWidget(self.status_label)

        self.detect_shorts_button = QPushButton("Detect Shorts")
        self.detect_shorts_button.clicked.connect(self.detect_shorts)
        layout.addWidget(self.detect_shorts_button)

        self.signal_received.connect(self.handle_signal)

        # Subscribe to backend messages
        self.setup_listeners()

    def detect_shorts(self):
        # Placeholder function to emit a message that shorts detection was triggered
        logger.info("Shorts detection triggered")

    def show_warning(self, title, message):
        QMessageBox.information(self, title, message)

    def setup_listeners(self):
        actor_topics_dict = {"dropbot_status_listener": ["dropbot/signals/+"]}
        self.router_actor = MessageRouterActor()
        self.dropbot_status_update_listener = self.create_dropbot_status_listener_actor()

        for actor_name, topics_list in actor_topics_dict.items():
            for topic in topics_list:
                self.router_actor.message_router_data.add_subscriber_to_topic(topic, actor_name)

    def handle_signal(self, message):
        topic, body = message.split(", ")
        if "connected" in topic:
            self.status_label.update_connection_status('connected')
        elif "disconnected" in topic:
            self.status_label.update_connection_status('disconnected')
        elif "chip_inserted" in topic:
            self.status_label.update_chip_status('chip_inserted')
        elif "chip_removed" in topic:
            self.status_label.update_chip_status('chip_removed')
        elif "no_power" in topic:
            self.show_warning('WARNING: no_power', f'{body}')
        elif "no_db_available" in topic:
            self.show_warning('WARNING: no_db_available', f'{body}')

    def create_dropbot_status_listener_actor(self):
        @dramatiq.actor
        def dropbot_status_listener(message, topic):
            logger.info(f"UI_LISTENER: Received message: {message} from topic: {topic}")
            topic_elements = topic.split("/")
            if topic_elements[-1] in ['connected', 'disconnected', 'chip_inserted', 'chip_removed', 'no_power',
                                      'no_db_available']:
                self.signal_received.emit(f"{topic}, {message}")

        return dropbot_status_listener



if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = DropBotControlWidget()
    widget.show()
    sys.exit(app.exec())