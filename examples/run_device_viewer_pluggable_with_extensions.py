# Plugin imports.
import sys

from envisage.api import CorePlugin
from envisage.ui.tasks.api import TasksPlugin


def main(args):
    """Run the application."""

    from examples.plugins.frontend import DeviceViewerPlugin
    from examples.plugins.frontend import DeviceViewerApplication
    from examples.plugins.frontend.device_viewer_extensions.manual_controls.plugin import ManualControlsPlugin

    plugins = [CorePlugin(), TasksPlugin(), DeviceViewerPlugin(), ManualControlsPlugin()]
    app = DeviceViewerApplication(plugins=plugins)
    app.run()


if __name__ == "__main__":
    import sys
    main(sys.argv)
