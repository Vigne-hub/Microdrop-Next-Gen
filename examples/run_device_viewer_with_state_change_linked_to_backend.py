# Plugin imports.

from envisage.api import CorePlugin
from envisage.ui.tasks.api import TasksPlugin
from microdrop_utils.broker_server_helpers import dramatiq_broker_context


def main(args):
    """Run the application."""

    from device_viewer.application import DeviceViewerApplication
    from device_viewer.plugin import DeviceViewerPlugin
    from dropbot_status.plugin import DropbotStatusPlugin
    from message_router.plugin import MessageRouterPlugin
    from dropbot_controller.plugin import DropbotControllerPlugin
    from electrode_controller.plugin import ElectrodeControllerPlugin

    plugins = [CorePlugin(), TasksPlugin(), DeviceViewerPlugin(), DropbotStatusPlugin(),
               MessageRouterPlugin(), DropbotControllerPlugin(), ElectrodeControllerPlugin()]

    app = DeviceViewerApplication(plugins=plugins)

    with dramatiq_broker_context():
        app.run()


if __name__ == "__main__":
    import sys
    import os

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    main(sys.argv)