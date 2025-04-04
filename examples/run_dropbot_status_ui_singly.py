# Plugin imports.

from envisage.api import CorePlugin
from envisage.ui.tasks.api import TasksPlugin

from microdrop_utils.broker_server_helpers import dramatiq_workers


def main(args):
    """Run the application."""

    from dropbot_status.plugin import DropbotStatusPlugin
    from message_router.plugin import MessageRouterPlugin
    from BlankMicrodropCanvas.plugin import BlankMicrodropCanvasPlugin

    from BlankMicrodropCanvas.application import MicrodropCanvasTaskApplication

    plugins = [
        CorePlugin(),
        TasksPlugin(),
        BlankMicrodropCanvasPlugin(),
        DropbotStatusPlugin(task_id_to_contribute_view="microdrop_canvas.task"),
        MessageRouterPlugin(),
    ]

    app = MicrodropCanvasTaskApplication(plugins=plugins)

    with dramatiq_workers():
        app.run()


if __name__ == "__main__":
    import sys
    import os

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    main(sys.argv)
