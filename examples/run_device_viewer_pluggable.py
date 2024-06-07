# Plugin imports.
from envisage.api import CorePlugin
from envisage.ui.tasks.api import TasksPlugin
import os
import sys

def main():
    """Run the application."""
    # Import here so that this script can be run from anywhere without
    # having to install the packages.

    from examples.plugins.frontend.qt_widgets.device_viewer.plugin import DeviceViewerPlugin
    from examples.plugins.frontend.qt_widgets.device_viewer.application import DeviceViewerApplication

    plugins = [CorePlugin(), TasksPlugin(), DeviceViewerPlugin()]
    app = DeviceViewerApplication(plugins=plugins)
    app.run()


if __name__ == "__main__":
    import os

    # This context manager is added so that one can run this example from any
    # directory without necessarily having installed the examples as packages.
    from envisage.examples._demo import demo_path

    with demo_path(__file__):
        main()

