import os
import sys

from envisage.api import CorePlugin
from envisage.ui.tasks.api import TasksPlugin

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from microdrop_utils.broker_server_helpers import dramatiq_workers_context, redis_server_context


def main(args):
    """Run the application."""

    from device_viewer.application import DeviceViewerApplication
    from device_viewer.plugin import DeviceViewerPlugin
    from dropbot_status.plugin import DropbotStatusPlugin
    from message_router.plugin import MessageRouterPlugin
    from dropbot_controller.plugin import DropbotControllerPlugin
    from manual_controls.plugin import ManualControlsPlugin
    from electrode_controller.plugin import ElectrodeControllerPlugin
    from dropbot_tools_menu.plugin import DropbotToolsMenuPlugin
    from dropbot_status_plot.plugin import DropbotStatusPlotPlugin

    plugins = [
        CorePlugin(),
        TasksPlugin(),
        DeviceViewerPlugin(),
        DropbotStatusPlugin(),
        ElectrodeControllerPlugin(),
        MessageRouterPlugin(),
        DropbotControllerPlugin(),
        ManualControlsPlugin(),
        DropbotToolsMenuPlugin(),
        DropbotStatusPlotPlugin()
    ]

    app = DeviceViewerApplication(plugins=plugins)

    with redis_server_context(), dramatiq_workers_context():
        app.run()


if __name__ == "__main__":
    main(sys.argv)