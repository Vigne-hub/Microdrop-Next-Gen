# Plugin imports.
import sys

from envisage.api import CorePlugin
from envisage.ui.tasks.api import TasksPlugin


def main(args):
    """Run the application."""

    from examples.plugins.frontend import DeviceViewerPlugin
    from examples.plugins.frontend import DeviceViewerApplication

    plugins = [CorePlugin(), TasksPlugin(), DeviceViewerPlugin()]
    app = DeviceViewerApplication(plugins=plugins)
    app.run()


if __name__ == "__main__":
    import sys
    main(sys.argv)
