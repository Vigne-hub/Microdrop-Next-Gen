# Plugin imports.
from envisage.api import CorePlugin
from envisage.ui.tasks.api import TasksPlugin


def main():
    """Run the application."""
    # Import here so that this script can be run from anywhere without
    # having to install the packages.

    from envisage_sample.widgets.device_viewer.plugin import DeviceViewerPlugin
    from envisage_sample.widgets.device_viewer.application import DeviceViewerApplication

    plugins = [CorePlugin(), TasksPlugin(), DeviceViewerPlugin()]
    app = DeviceViewerApplication(plugins=plugins)
    app.run()


if __name__ == "__main__":
    import sys
    main()