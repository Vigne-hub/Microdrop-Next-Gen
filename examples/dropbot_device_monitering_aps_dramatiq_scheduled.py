import sys
import base_node_rpc as bnr
from traits.api import HasTraits, Str, Callable, Union

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

            except Exception as e:
                print(f'Error: {e}')

        return check_dropbot_devices_available_actor


def main(args):
    example_instance = DropBotDeviceConnectionMonitor()
    scheduler = BlockingScheduler()
    scheduler.add_job(
        example_instance.check_dropbot_devices_available_actor.send,
        IntervalTrigger(seconds=2),
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
