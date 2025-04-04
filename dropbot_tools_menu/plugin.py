# enthought imports
from functools import partial

from pyface.action.schema.schema_addition import SchemaAddition
from traits.api import List, observe, Str
from envisage.api import Plugin, TASK_EXTENSIONS
from envisage.ui.tasks.api import TaskExtension
from message_router.consts import ACTOR_TOPIC_ROUTES
from device_viewer.consts import PKG as device_viewer_PKG

from .consts import ACTOR_TOPIC_DICT, PKG, PKG_name
from .device_viewer_task_method_additions import _on_self_tests_progress_triggered


class DropbotToolsMenuPlugin(Plugin):
    """ Contributes UI actions on top of the IPython Kernel Plugin. """

    #### 'IPlugin' interface ##################################################

    #: The plugin unique identifier.
    id = PKG + ".plugin"

    #: The plugin name (suitable for displaying to the user).
    name = f"{PKG_name} Plugin"

    #### Contributions to extension points made by this plugin ################

    contributed_task_extensions = List(contributes_to=TASK_EXTENSIONS)

    # This plugin wants some actors to be called using certain routing keys.
    actor_topic_routing = List([ACTOR_TOPIC_DICT], contributes_to=ACTOR_TOPIC_ROUTES)

    #: The task id to contribute task extension view to
    task_id_to_contribute_view = Str(default_value=f"{device_viewer_PKG}.task")

    #### Trait initializers ###################################################

    def _contributed_task_extensions_default(self):
        from .menus import dropbot_tools_menu_factory

        return [
            TaskExtension(
                task_id=self.task_id_to_contribute_view,
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
            if task.id == f"{device_viewer_PKG}.task":
                setattr(task, _on_self_tests_progress_triggered.__name__,
                        partial(_on_self_tests_progress_triggered, task))