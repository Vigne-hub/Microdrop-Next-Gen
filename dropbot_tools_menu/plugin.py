# enthought imports
from functools import partial

from pyface.action.schema.schema_addition import SchemaAddition
from traits.api import List, observe
from envisage.api import Plugin, TASK_EXTENSIONS
from envisage.ui.tasks.api import TaskExtension
from message_router.consts import ACTOR_TOPIC_ROUTES

from .consts import ACTOR_TOPIC_DICT, PKG
from .device_viewer_task_method_additions import _on_self_tests_progress_triggered


class DropbotToolsMenuPlugin(Plugin):
    """ Contributes UI actions on top of the IPython Kernel Plugin. """

    #### 'IPlugin' interface ##################################################

    #: The plugin unique identifier.
    id = PKG + ".plugin"

    #: The plugin name (suitable for displaying to the user).
    name = "Dropbot Tools Menu Plugin"

    #### Contributions to extension points made by this plugin ################

    contributed_task_extensions = List(contributes_to=TASK_EXTENSIONS)

    # This plugin wants some actors to be called using certain routing keys.
    actor_topic_routing = List([ACTOR_TOPIC_DICT], contributes_to=ACTOR_TOPIC_ROUTES)

    #### Trait initializers ###################################################

    def _contributed_task_extensions_default(self):
        from .menus import dropbot_tools_menu_factory



        return [
            TaskExtension(
                task_id="device_viewer.task",
                actions=[
                    SchemaAddition(
                        factory=dropbot_tools_menu_factory,
                        path='MenuBar/Tools',
                    )

                ]
            )
        ]

    @observe("application:application_initialized")
    def on_application_initialized(self, event):
        # add some listener methods to the application task
        for task in self.application.active_window.tasks:
            if task.id == "device_viewer.task":
                setattr(task, _on_self_tests_progress_triggered.__name__,
                        partial(_on_self_tests_progress_triggered, task))