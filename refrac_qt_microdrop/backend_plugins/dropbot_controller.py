import numpy as np
from typing import Union
from envisage.api import Plugin, ServiceOffer
from traits.api import List
import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
import dropbot
import serial
import logging
from refrac_qt_microdrop.interfaces import IDropbotControllerService

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

rabbitmq_broker = RabbitmqBroker(url="amqp://guest:guest@localhost/")
dramatiq.set_broker(rabbitmq_broker)


class DropbotControllerPlugin(Plugin):
    id = 'refrac__qt_microdrop.dropbot_controller'
    name = 'Dropbot Plugin'
    service_offers = List(contributes_to='envisage.service_offers')

    def start(self):
        super().start()
        self._register_services()
        logger.info("DropbotController Plugin started")

    def _register_services(self):
        dropbot_service = self._create_service()
        self.application.register_service(IDropbotControllerService, dropbot_service)

        self._start_worker()

    def _service_offers_default(self):
        return [
            ServiceOffer(protocol=IDropbotControllerService, factory=self._create_service)
        ]

    def _create_service(self, *args, **kwargs):
        from refrac_qt_microdrop.services import DropbotService
        return DropbotService()

    def _start_worker(self):
        import threading
        from dramatiq import Worker

        worker = Worker(broker=rabbitmq_broker)
        worker_thread = threading.Thread(target=worker.start())
        worker_thread.daemon = True
        worker_thread.start()


class DropbotControllerLogic:
    def __init__(self):
        self.proxy: Union[None, dropbot.SerialProxy] = None
        self.last_state = np.zeros(128, dtype='uint8')
        self.init_dropbot_proxy()

    def init_dropbot_proxy(self):
        try:
            port = serial.serial_for_url('hwgrep://USB Serial', do_not_open=True).port
            self.proxy = dropbot.SerialProxy(port=port)
        except (IOError, AttributeError):
            self.proxy = None
            return False

        self.proxy.hv_output_enabled = False
        self.proxy.voltage = 0
        self.proxy.frequency = 10000
        self.last_state = np.array(self.proxy.state_of_channels)
        self.last_state = self.get_channels()

        OUTPUT_ENABLE_PIN = 22
        if self.proxy.digital_read(OUTPUT_ENABLE_PIN):
            self.notify_output_state_changed(False)
        else:
            self.notify_output_state_changed(True)
        return True

    @dramatiq.actor(queue_name='notifications')
    def notify_output_state_changed(self, state: bool):
        logger.info(f"Output state changed: {state}")
        # Publish to a specific queue for notifications

    @dramatiq.actor
    def poll_voltage(self):
        if self.proxy is not None:
            try:
                voltage = self.proxy.high_voltage()
                self.notify_voltage_changed(voltage)
            except OSError:
                pass

    @dramatiq.actor(queue_name='notifications')
    def notify_voltage_changed(self, voltage: float):
        logger.info(f"Voltage changed: {voltage}")
        # Publish to a specific queue for notifications

    @dramatiq.actor
    def set_voltage(self, voltage=int):
        if self.proxy is not None:
            self.proxy.voltage = voltage
        logger.info(f"Voltage set to {voltage}")

    @dramatiq.actor
    def set_frequency(self, frequency: int):
        if self.proxy is not None:
            self.proxy.frequency = frequency
        logger.info(f"Frequency set to {frequency}")

    @dramatiq.actor
    def set_hv(self, on: bool):
        if self.proxy is not None:
            self.proxy.hv_output_enabled = on

    @dramatiq.actor
    def get_channels(self):
        if self.proxy is None:
            return np.zeros(128, dtype='uint8')

        channels = np.array(self.proxy.state_of_channels)
        if (self.last_state != channels).any():
            self.last_state = channels
            self.notify_channels_changed(channels)
        return channels

    @dramatiq.actor
    def notify_channels_changed(self, channels):
        logger.info(f"Channels changed: {channels}")
        # Publish to a specific queue for notifications

    @dramatiq.actor
    def set_channels(self, channels):
        if self.proxy is None:
            return
        self.proxy.state_of_channels = np.array(channels)
        self.last_state = self.get_channels()

    @dramatiq.actor
    def set_channel_single(self, channel: int, state: bool):
        if self.proxy is None:
            return
        channels = self.get_channels()
        channels[channel] = state
        self.set_channels(channels)

    @dramatiq.actor
    def droplet_search(self, threshold: float = 0):
        if self.proxy is not None:
            self.set_channels(np.zeros_like(self.last_state))
            drops = list(self.last_state)
            for drop in self.proxy.get_drops(capacitance_threshold=threshold):
                for electrode in drop:
                    drops[electrode] = 'droplet'
            self.notify_channels_metastate_changed(drops)

    @dramatiq.actor(queue_name='notifications')
    def notify_channels_metastate_changed(self, drops):
        logger.info(f"Channels metastate changed: {drops}")
