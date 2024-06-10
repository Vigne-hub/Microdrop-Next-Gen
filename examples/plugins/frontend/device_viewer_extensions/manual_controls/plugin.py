# enthought imports
from traits.api import List
from envisage.api import Plugin
from envisage.ui.tasks.api import TaskExtension

TASK_EXTENSIONS = "envisage.ui.tasks.task_extensions"


class ManualControlsPlugin(Plugin):
    """ Contributes UI actions on top of the IPython Kernel Plugin. """

    #### 'IPlugin' interface ##################################################

    #: The plugin unique identifier.
    id = "manual_controls.plugin"

    #: The plugin name (suitable for displaying to the user).
    name = "IPython embedded kernel UI plugin"

    #### Contributions to extension points made by this plugin ################

    contributed_task_extensions = List(contributes_to=TASK_EXTENSIONS)

    #### Trait initializers ###################################################

    def _contributed_task_extensions_default(self):

        from .DockPane import ManualControlsDockPane

        return [
            TaskExtension(
                task_id="device_viewer.task",
                dock_pane_factories=[ManualControlsDockPane]
            )
        ]