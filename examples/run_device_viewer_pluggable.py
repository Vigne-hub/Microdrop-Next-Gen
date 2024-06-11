# Plugin imports.
import sys

from envisage.api import CorePlugin
from envisage.ui.tasks.api import TasksPlugin


def main(args):
    """Run the application."""

    from plugins.frontend import DeviceViewerPlugin
    from plugins.frontend import DeviceViewerApplication

    plugins = [CorePlugin(), TasksPlugin(), DeviceViewerPlugin()]
    app = DeviceViewerApplication(plugins=plugins)
    app.run()


if __name__ == "__main__":
    import sys

    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    main(sys.argv)
