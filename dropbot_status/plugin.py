# enthought imports
from traits.api import List
from envisage.api import Plugin, TASK_EXTENSIONS
from envisage.ui.tasks.api import TaskExtension

from .consts import PKG


class DropbotStatusPlugin(Plugin):
    """ Contributes a dropbot status UI view. """

    #### 'IPlugin' interface ##################################################

    #: The plugin unique identifier.
    id = PKG + ".plugin"
    #: The plugin name (suitable for displaying to the user).
    name = "Dropbot Status Plugin"

    #### Contributions to extension points made by this plugin ################

    contributed_task_extensions = List(contributes_to=TASK_EXTENSIONS)

    #### Trait initializers ###################################################

    def _contributed_task_extensions_default(self):
        from .dock_pane import DropbotStatusDockPane

        return [
            TaskExtension(
                task_id="device_viewer.task",  # specify which task id it has to add on to
                dock_pane_factories=[DropbotStatusDockPane],
            )
        ]
