import sys
# import base_node_rpc as bnr
from traits.api import HasTraits, Str, Callable, List
from microdrop_utils.dramatiq_pub_sub_helpers import publish_message, MessageRouterActor
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
import dramatiq
from serial.tools.list_ports import grep
from microdrop_utils._logger import get_logger
import re

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
    for n, (port, desc, hwid) in enumerate(connected_ports):
        teensy = re.match(f".*{id_to_screen}*", hwid)

        if bool(teensy):
            valid_ports.append(port)

    return valid_ports


class DropBotDeviceConnectionMonitor(HasTraits):
    check_dropbot_devices_available_actor = Callable
    # port = Str()
    hwids_to_check = List(Str())

    def _hwids_to_check_default(self):
        return ["VID:PID=16C0:"]

    def _check_dropbot_devices_available_actor_default(self):
        return self.create_check_dropbot_devices_available_actor()

    def create_check_dropbot_devices_available_actor(self):
        @dramatiq.actor
        def check_dropbot_devices_available_actor():

            # This is one method to find the usb port of the dropbot if it is connected.

            try:
                for hwid in self.hwids_to_check:
                    valid_ports = check_connected_ports_hwid(hwid)
                    if valid_ports:
                        port_names = [port.name for port in valid_ports]
                        publish_message(f'New dropbot found on ports: {port_names}', 'dropbot/ports')
                    else:
                        publish_message('No DropBot available for connection', 'dropbot/error')

            except Exception as e:
                publish_message(f'No DropBot available for connection with exception {e}', 'dropbot/error')

            # this is the other method. It can work with all ids as long as it is a dropbot.
            # so it avoids the need to know the id of the dropbot. But it needs to setup a conenction with the dropbot first.
            # This might be intensive of a task to do every second.

            # try:
            #
            #     # Find DropBots
            #     df_devices = bnr.available_devices(timeout=.5)
            #
            #     if not df_devices.shape[0]:
            #         self.port = ''
            #         raise IOError('No DropBot available for connection')
            #
            #     df_dropbots = df_devices.loc[df_devices.device_name.isin(['dropbot', b'dropbot'])]
            #
            #     if not df_dropbots.shape[0]:
            #         self.port = ''
            #         raise IOError('No DropBot available for connection')
            #
            #     port = df_dropbots.index[0]
            #
            #     if port != self.port:
            #         self.port = port
            #         publish_message(f'New dropbot found on port {port}', 'dropbot/port')
            #
            # except Exception as e:
            #     # print(f'Error: {e}')
            #     publish_message(str(e), 'dropbot/error')

        return check_dropbot_devices_available_actor


@dramatiq.actor
def print_dropbot_message(message=str, topic=str):
    print(f"PRINT_DROPBOT_MESSAGE_SERVICE: Received message: {message}! from topic: {topic}")


@dramatiq.actor
def make_serial_proxy(ports):
    import dropbot
    try:
        proxy = dropbot.SerialProxy(port=ports[0])
    except (IOError, AttributeError):
        publish_message('No DropBot available for connection', 'dropbot/error')


def main(args):
    message_router_actor = MessageRouterActor()

    message_router_actor.message_router_data.add_subscriber_to_topic('dropbot/#', 'print_dropbot_message')
    message_router_actor.message_router_data.add_subscriber_to_topic('dropbot/ports', 'make_serial_proxy')

    example_instance = DropBotDeviceConnectionMonitor()
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
        init_broker_server(BROKER)
        worker = Worker(BROKER, worker_threads=1)
        worker.start()
        main(sys.argv[1:])
    finally:
        worker.stop()
        stop_broker_server(BROKER)
