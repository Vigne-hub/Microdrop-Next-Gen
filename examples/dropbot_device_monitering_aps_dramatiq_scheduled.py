import sys
import base_node_rpc as bnr
from traits.api import HasTraits, Str, Callable, Union
from microdrop_utils.dramatiq_pub_sub_helpers import publish_message, MessageRouterActor
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

import dramatiq

# remove prometheus metrics for now
for el in dramatiq.get_broker().middleware:
    if el.__module__ == "dramatiq.middleware.prometheus":
        dramatiq.get_broker().middleware.remove(el)


class DropBotDeviceConnectionMonitor(HasTraits):
    check_dropbot_devices_available_actor = Callable
    port = Str()

    def _port_default(self):
        return ''
    def _check_dropbot_devices_available_actor_default(self):
        return self.create_check_dropbot_devices_available()

    def create_check_dropbot_devices_available(self):
        @dramatiq.actor
        def check_dropbot_devices_available_actor():

            try:

                # Find DropBots
                df_devices = bnr.available_devices(timeout=.5)
                if not df_devices.shape[0]:
                    raise IOError('No DropBot available for connection')
                df_dropbots = df_devices.loc[df_devices.device_name.isin(['dropbot', b'dropbot'])]
                if not df_dropbots.shape[0]:
                    raise IOError('No DropBot available for connection')
                port = df_dropbots.index[0]

                print(f'Found DropBot on port {port}')

                if port != self.port:
                    self.port = port
                    print(f'New dropbot found on port {port}')
                    publish_message(port, 'dropbot/port')

            except Exception as e:
               # print(f'Error: {e}')
                publish_message(str(e), 'dropbot/error')

        return check_dropbot_devices_available_actor

@dramatiq.actor
def print_dropbot_message(message=str, topic=str):
    print(f"PRINT_DROPBOT_MESSAGE_SERVICE: Received message: {message}! from topic: {topic}")


def main(args):

    message_router_actor = MessageRouterActor()

    message_router_actor.message_router_data.add_subscriber_to_topic('dropbot/#', 'print_dropbot_message')

    example_instance = DropBotDeviceConnectionMonitor()
    scheduler = BlockingScheduler()
    scheduler.add_job(
        example_instance.check_dropbot_devices_available_actor.send,
        IntervalTrigger(seconds=0.2),
    )
    try:
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.shutdown()

    return 0


if __name__ == "__main__":
    from dramatiq import Worker

    worker = Worker(dramatiq.get_broker(), worker_threads=1)
    worker.start()
    sys.exit(main(sys.argv))
