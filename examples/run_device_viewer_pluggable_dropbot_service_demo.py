# Plugin imports.
from envisage.api import CorePlugin
from envisage.application import Application
from dropbot_controller.plugin import DropbotControllerPlugin
from examples.plugins.backend.toy_service_plugins.dummy_dropbot.plugin import DummyDropbotServicePlugin


class ExampleApp(Application):
    def __init__(self, plugins, broker=None):
        super().__init__(plugins=plugins)


def main(args):
    """Run the application."""

    plugins = [CorePlugin(), DropbotControllerPlugin(), DummyDropbotServicePlugin()]
    app = ExampleApp(plugins=plugins)
    app.run()


if __name__ == "__main__":
    import sys

    import os

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    main(sys.argv)
