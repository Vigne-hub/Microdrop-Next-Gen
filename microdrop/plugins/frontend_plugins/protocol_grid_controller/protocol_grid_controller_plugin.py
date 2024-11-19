# enthought imports
from pyface.action.schema.schema_addition import SchemaAddition
from traits.api import List
from envisage.api import Plugin, TASK_EXTENSIONS
from envisage.ui.tasks.api import TaskExtension

from microdrop_utils.dramatiq_pub_sub_helpers import MessageRouterActor

# This module's package.
PKG = '.'.join(__name__.split('.')[:-1])


class ProtocolGridControllerPlugin(Plugin):
    """ Contributes UI actions on top of the IPython Kernel Plugin. """

    #### 'IPlugin' interface ##################################################

    #: The plugin unique identifier.
    id = PKG + ".plugin"

    #: The plugin name (suitable for displaying to the user).
    name = "Protocol Grid Controller Plugin"

    #### Contributions to extension points made by this plugin ################

    contributed_task_extensions = List(contributes_to=TASK_EXTENSIONS)

    #### Trait initializers ###################################################

    def _contributed_task_extensions_default(self):
        from .protocol_grid_controller_pane import PGCDockPane

        return [
            TaskExtension(
                task_id="device_viewer.task",
                dock_pane_factories=[PGCDockPane]
            )
        ]

    def start(self):
        super().start() # starts plugin service
        # self.protocol_grid = self._create_service() # gets services
        # self.register_subscribers() # registers subscribers
        # self._start_worker() # starts worker for

    # def _create_service(self):
    #     from microdrop.services.dropbot_services import DropbotService
    #     return DropbotService()

    # def register_subscribers(self):
    #     self.message_router = self.application.get_service(MessageRouterActor)
    #     if self.message_router is not None:
    #         # Use the message_router_actor instance as needed
    #         print("MessageRouterActor service accessed successfully.")
    #         for actor_name, topics_list in self.dropbot_service.actor_topics_dict.items():
    #             for topic in topics_list:
    #                 # figure out how to set up message router plugin
    #                 self.message_router.message_router_data.add_subscriber_to_topic(topic, actor_name)
    #     else:
    #         print("MessageRouterActor service not found.")
    #         return