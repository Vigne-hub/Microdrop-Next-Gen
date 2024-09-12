# Plugin imports.

from envisage.api import CorePlugin
from envisage.ui.tasks.api import TasksPlugin

from device_viewer.application import DeviceViewerApplication
from device_viewer.plugin import DeviceViewerPlugin
from dropbot_status.plugin import DropbotStatusPlugin
from manual_controls.plugin import ManualControlsPlugin


def main(args):
    """Run the application."""

    plugins = [CorePlugin(), TasksPlugin(), DeviceViewerPlugin(), ManualControlsPlugin(), DropbotStatusPlugin()]
    app = DeviceViewerApplication(plugins=plugins)
    app.run()


if __name__ == "__main__":
    import sys
    import os

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    main(sys.argv)
