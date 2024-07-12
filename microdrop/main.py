# main.py
import sys
from PySide6.QtWidgets import QApplication
from envisage.api import Application, CorePlugin
from envisage.ui.tasks.api import TasksPlugin

from .plugins.frontend_plugins.protocol_grid_controller.protocol_grid_controller_plugin import \
    ProtocolGridControllerPlugin
from .plugins.backend_plugins.protocol_grid_controller import ProtocolGridBackendPlugin
from microdrop_utils.dramatiq_pub_sub_helpers import MessageRouterActor
from .plugins.backend_plugins.dropbot_controller import DropbotControllerPlugin
from .app import MicroDropApplication
from .plugins.frontend_plugins.device_viewer.plugin import DeviceViewerPlugin
from .plugins.frontend_plugins.dropbot_status.dropbot_status_plugin import DropbotStatusPlugin
from microdrop_utils.rmq_purger import RmqPurger
import atexit

def main():
    purger = RmqPurger()
    message_router = MessageRouterActor()

    plugins = [CorePlugin(),
               TasksPlugin(),
               DeviceViewerPlugin(),
               #DropbotStatusPlugin(),
               #DropbotControllerPlugin(),
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
