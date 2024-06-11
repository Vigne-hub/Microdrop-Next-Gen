# enthought imports
from traits.api import List
from envisage.api import Plugin, TASK_EXTENSIONS
from envisage.ui.tasks.api import TaskExtension

# This module's package.
PKG = '.'.join(__name__.split('.')[:-1])

class ManualControlsPlugin(Plugin):
    """ Contributes UI actions on top of the IPython Kernel Plugin. """

    #### 'IPlugin' interface ##################################################

    #: The plugin unique identifier.
    id = PKG + ".plugin"

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