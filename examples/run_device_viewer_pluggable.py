# Plugin imports.
from envisage.api import CorePlugin
from envisage.ui.tasks.api import TasksPlugin


def main():
    """Run the application."""

    from examples.plugins.frontend import DeviceViewerPlugin
    from examples.plugins.frontend.qt_widgets.device_viewer.application import DeviceViewerApplication

    plugins = [CorePlugin(), TasksPlugin(), DeviceViewerPlugin()]
    app = DeviceViewerApplication(plugins=plugins)
    app.run()


if __name__ == "__main__":
    main()
