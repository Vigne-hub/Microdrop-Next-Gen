import sys

# import base_node_rpc as bnr
from traits.api import HasTraits, Str, Callable, List, Instance
from microdrop_utils.dramatiq_pub_sub_helpers import publish_message, MessageRouterActor
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
import dramatiq
from serial.tools.list_ports import grep
from microdrop_utils._logger import get_logger
import re

from microdrop_utils.pub_sub_serial_proxy import DropbotSerialProxy

logger = get_logger(__name__)


def check_connected_ports_hwid(id_to_screen, regexp='USB Serial'):
    """
    Check connected USB ports for a specific hardware id.
    """

    # get connected ports to usb serial
    connected_ports = grep(regexp)

    # initialize list to store valid ports
    valid_ports = []

    # go through connected ports and check if the hardware id matches the id
    # try using regex: neglect PID use the VID
    for port in connected_ports:
        # Regex pattern to find the VID in the hwid string
        pattern = re.compile(f".*{id_to_screen}.*")

        # Search for the pattern in the string
        teensy = re.search(pattern, port.hwid)

        if bool(teensy):
            valid_ports.append(port)

    return valid_ports


class DropbotSearcher(HasTraits):
    check_dropbot_devices_available_actor = Callable
    port_names = List(Str())
    hwids_to_check = List(Str())

    def _hwids_to_check_default(self):
        return ["VID:PID=16C0:"]

    def _check_dropbot_devices_available_actor_default(self):
        return self.create_check_dropbot_devices_available_actor()

    def create_check_dropbot_devices_available_actor(self):
        @dramatiq.actor
        def check_dropbot_devices_available_actor():
            """
            Method to find the USB port of the DropBot if it is connected.
            """
            try:
                # Iterate through the hardware IDs to check
                for hwid in self.hwids_to_check:

                    # Find the valid ports for the hardware ID
                    valid_ports = check_connected_ports_hwid(hwid)

                    # Check if there are valid ports
                    if valid_ports:
                        print(f"Found DropBot connected to port: {valid_ports[0].name}")

                        # Extract port names
                        port_names = [port.name for port in valid_ports]

                        publish_message(port_names, 'dropbot/ports')

            except Exception as e:
                # reset the port names list to capture reconnection in the same port.
                self.port_names = []
                print(f'No DropBot available for connection with exception {e}', 'dropbot/error')

        return check_dropbot_devices_available_actor


@dramatiq.actor
def print_dropbot_message(message=str, topic=str):
    print(f"PRINT_DROPBOT_MESSAGE_SERVICE: Received message: {message}! from topic: {topic}")


def main(args):
    message_router_actor = MessageRouterActor()

    message_router_actor.message_router_data.add_subscriber_to_topic('dropbot/#', 'print_dropbot_message')
    #message_router_actor.message_router_data.add_subscriber_to_topic('dropbot/ports', 'make_serial_proxy')

    example_instance = DropbotSearcher()
    scheduler = BlockingScheduler()
    scheduler.add_job(
        example_instance.check_dropbot_devices_available_actor.send,
        IntervalTrigger(seconds=1),
    )
    try:
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.shutdown()

    return 0


if __name__ == "__main__":
    from dramatiq import Worker
    from examples.broker import BROKER

    from microdrop_utils.broker_server_helpers import init_broker_server, stop_broker_server

    try:
       # init_broker_server(BROKER)
        worker = Worker(BROKER)
        worker.start()
        main(sys.argv[1:])
    finally:
        BROKER.flush_all()
        worker.stop()
    #    stop_broker_server(BROKER)
