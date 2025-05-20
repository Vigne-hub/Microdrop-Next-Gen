import sys
import os
import signal
import time

from envisage.api import CorePlugin
from envisage.application import Application

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from microdrop_utils.broker_server_helpers import redis_server_context, dramatiq_workers_context


def main(args):
    """Run the application."""

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
    with redis_server_context(), dramatiq_workers_context():

        app.run()

        while True:
            time.sleep(0.001)


if __name__ == "__main__":
    main(sys.argv)
