# main.py
from envisage.api import CorePlugin
from envisage.ui.tasks.api import TasksPlugin

from examples.plugins.frontend import DeviceViewerPlugin
from microdrop.plugins.frontend_plugins.protocol_grid_controller.protocol_grid_controller_plugin import \
    ProtocolGridControllerPlugin
from microdrop.plugins.backend_plugins.protocol_grid_controller import ProtocolGridBackendPlugin
from microdrop_utils.dramatiq_pub_sub_helpers import MessageRouterActor
from microdrop.plugins.backend_plugins.dropbot_controller import DropbotControllerPlugin
from microdrop.app import MicroDropApplication
from dropbot_status import DropbotStatusPlugin
from microdrop_utils.rmq_purger import RmqPurger
import atexit


def main():
    purger = RmqPurger()
    message_router = MessageRouterActor()

    plugins = [CorePlugin(),
               TasksPlugin(),
               DeviceViewerPlugin(),
               DropbotStatusPlugin(),
               DropbotControllerPlugin(),
               ProtocolGridBackendPlugin(),
               ProtocolGridControllerPlugin()
               ]
    app = MicroDropApplication(plugins=plugins)

    app.register_service(MessageRouterActor, message_router)
    atexit.register(on_exit, purger)
    app.run()

    # plugins = []
    # envisage_app = Application(plugins=plugins)
    # envisage_app.run()


def on_exit(purger):
    purger.purge_all_queues()


if __name__ == '__main__':
    main()
