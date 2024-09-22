from .dramatiq_pub_sub_helpers import publish_message
from dropbot.proxy import SerialProxy
import base_node_rpc as bnr
import functools as ft


class DramatiqDropbotSerialProxy(SerialProxy):

    def connect(self):
        self.terminate()

        # We need to signal to the dramatiq pub sub system that the dropbot has been disconnected/connected we are
        # writing a wrapper will still do everything the original monitor function does except for the dramatiq pub
        # sub publishing of the message this wrapper takes care of.

        # define the dramatiq pub sub wrappers
        def publish_wrapper(f, signal_name):
            f()
            publish_message(f'dropbot_{signal_name}', f"dropbot/signals/{signal_name}")

        monitor = bnr.ser_async.BaseNodeSerialMonitor(port=self.port)

        monitor.connected_event.set = ft.partial(publish_wrapper, monitor.connected_event.set, 'connected')
        monitor.disconnected_event.set = ft.partial(publish_wrapper, monitor.disconnected_event.set, 'disconnected')

        monitor.start()

        monitor.connected_event.wait()
        self.monitor = monitor
        return self.monitor
