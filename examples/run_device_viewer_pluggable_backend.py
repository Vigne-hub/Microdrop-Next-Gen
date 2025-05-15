# Plugin imports.
import signal
import time

import dramatiq
from dramatiq import Worker
from envisage.api import CorePlugin
from envisage.application import Application


def main(args):
    """Run the application."""

    from dropbot_controller.consts import START_DEVICE_MONITORING
    from microdrop_utils.dramatiq_pub_sub_helpers import publish_message
    from message_router.plugin import MessageRouterPlugin
    from dropbot_controller.plugin import DropbotControllerPlugin
    from electrode_controller.plugin import ElectrodeControllerPlugin

    plugins = [
        CorePlugin(),
        MessageRouterPlugin(),
        ElectrodeControllerPlugin(),
        DropbotControllerPlugin(),
    ]

    app = Application(plugins=plugins)

    def stop_app(signum, frame):
        print("Shutting down...")
        app.stop()
        exit(0)

        # Register signal handlers

    signal.signal(signal.SIGINT, stop_app)
    signal.signal(signal.SIGTERM, stop_app)

    # Need to run with a dramatiq broker context since app requires plugins that use dramatiq
    with dramatiq_workers():

        app.run()

        while True:
            time.sleep(0.001)


if __name__ == "__main__":
    import sys
    import os

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from microdrop_utils.broker_server_helpers import dramatiq_workers

    main(sys.argv)
