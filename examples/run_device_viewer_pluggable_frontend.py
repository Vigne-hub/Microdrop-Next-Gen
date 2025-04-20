# Plugin imports.
from envisage.api import CorePlugin
from envisage.ui.tasks.api import TasksPlugin


def main(args):
    """Run the application."""

    from device_viewer.application import DeviceViewerApplication
    from device_viewer.plugin import DeviceViewerPlugin
    from dropbot_status.plugin import DropbotStatusPlugin
    from message_router.plugin import MessageRouterPlugin
    from manual_controls.plugin import ManualControlsPlugin
    from protocol_grid_controller_ui.protocol_grid_controller_plugin import ProtocolGridControllerPlugin
    from dropbot_tools_menu.plugin import DropbotToolsMenuPlugin

    plugins = [
        CorePlugin(),
        TasksPlugin(),
        DeviceViewerPlugin(),
        DropbotStatusPlugin(),
        MessageRouterPlugin(),
        ManualControlsPlugin(),
        ProtocolGridControllerPlugin(),
        DropbotToolsMenuPlugin()
    ]

    app = DeviceViewerApplication(plugins=plugins)

    # # Need to run with a dramatiq broker context since app requires plugins that use dramatiq
    with dramatiq_workers():
        app.run()


if __name__ == "__main__":
    import sys
    import os

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from microdrop_utils.broker_server_helpers import dramatiq_workers

    main(sys.argv)