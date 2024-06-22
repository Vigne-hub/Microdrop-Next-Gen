# system imports
import functools
import re
from typing import Union

# ap scheduler imports
from apscheduler.events import EVENT_JOB_EXECUTED
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from traits.has_traits import HasTraits, provides
import dramatiq
import dropbot

# local imports
from microdrop.interfaces import IDropbotControllerService
from microdrop_utils.dramatiq_pub_sub_helpers import publish_message
from microdrop_utils._logger import get_logger
from microdrop_utils.pub_sub_serial_proxy import DropbotSerialProxy
from .dropbot_service_helpers import check_dropbot_devices_available

logger = get_logger(__name__)


@provides(IDropbotControllerService)
class DropbotService(HasTraits):

    def __init__(self):
        logger.info('Initializing dropbot services')

        self.make_serial_proxy = self._make_serial_proxy()
        self.ui_listener = self.create_dropbot_backend_listener_actor()

        # actor_topics
        self.actor_topics_dict = {"dropbot_backend_listener": ["dropbot/signals/+"]}

        self.proxy: Union[DropbotSerialProxy, None] = None

        hwids_to_check = ["VID:PID=16C0:"]

        scheduler = BackgroundScheduler()
        scheduler.add_job(
            func=functools.partial(check_dropbot_devices_available, hwids_to_check),
            trigger=IntervalTrigger(seconds=2),
        )
        scheduler.add_listener(self.on_dropbot_port_found, EVENT_JOB_EXECUTED)
        self.scheduler = scheduler

    def on_dropbot_port_found(self, event):
        logger.info("DropBot port found")
        logger.info('Attempting to make serial proxy for DropBot')
        self.scheduler.pause()
        port_name = str(event.retval)
        self.make_serial_proxy.send(port_name)

    def on_disconnected(self):
        self.scheduler.resume()
        publish_message(topic='dropbot/ui/signals/disconnected', message='DropBot disconnected')

    def on_connected(self):
        self.scheduler.pause()
        publish_message(topic='dropbot/ui/signals/connected', message='DropBot connected')

    def _make_serial_proxy(self):
        logger.info("Creating serial proxy function")

        @dramatiq.actor
        def make_serial_proxy(port_name):
            logger.info(f"Attempting to create serial proxy")
            try:
                self.proxy = DropbotSerialProxy(port=port_name)
                logger.info(f"Connected to DropBot on port {port_name}")
                self.setup_dropbot()
            except (IOError, AttributeError):
                publish_message(topic='dropbot/ui/connection/warnings/no_dropbot_available',
                                message='No DropBot available for connection')
                logger.error("No DropBot available for connection")
            except dropbot.proxy.NoPower:
                publish_message(topic='dropbot/ui/connection/warnings/no_power', message='No power to DropBot')
                logger.error("No power to DropBot")

        logger.info('Completed making serial proxy')
        return make_serial_proxy

    def create_dropbot_backend_listener_actor(self):
        """
        Create a Dramatiq actor for listening to UI-related messages.

        Returns:
        dramatiq.Actor: The created Dramatiq actor.
        """

        @dramatiq.actor
        def dropbot_backend_listener(message, topic):
            """
            A Dramatiq actor that listens to UI-related messages.

            Parameters:
            message (str): The received message.
            topic (str): The topic of the message.
            """
            logger.info(f"DROPBOT BACKEND LISTENER: Received message: {message} from topic: {topic}")

            topic = topic.split("/")

            if topic[-1] == "connected":
                self.on_connected()

            if topic[-1] == "disconnected":
                if self.proxy is not None:
                    if self.proxy.monitor is not None:
                        self.proxy.terminate()
                        self.proxy.monitor = None
                        self.on_disconnected()
                else:
                    print("Proxy is None")

        return dropbot_backend_listener

    def setup_dropbot(self):
        OUTPUT_ENABLE_PIN = 22
        if self.proxy.digital_read(OUTPUT_ENABLE_PIN):
            publish_message(topic='dropbot/ui/signals/chip_not_inserted', message='Chip not inserted')
        else:
            publish_message(topic='dropbot/ui/signals/chip_inserted', message='Chip inserted')

        self.proxy.signals.signal('output_enabled').connect(self.output_state_changed_wrapper)
        self.proxy.signals.signal('output_disabled').connect(self.output_state_changed_wrapper)

    def output_state_changed_wrapper(self, signal: dict[str, str]):
        if signal['event'] == 'output_enabled':
            publish_message(topic='dropbot/ui/signals/chip_inserted', message='Chip inserted')
        elif signal['event'] == 'output_disabled':
            publish_message(topic='dropbot/ui/signals/chip_not_inserted', message='Chip not inserted')
        else:
            logger.warn(f"Unknown signal received: {signal}")
