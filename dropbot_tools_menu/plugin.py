# enthought imports
from pyface.action.schema.schema_addition import SchemaAddition
from traits.api import List
from envisage.api import Plugin, TASK_EXTENSIONS
from envisage.ui.tasks.api import TaskExtension

# This module's package.
PKG = '.'.join(__name__.split('.')[:-1])

class DropbotToolsMenuPlugin(Plugin):
    """ Contributes UI actions on top of the IPython Kernel Plugin. """

    #### 'IPlugin' interface ##################################################

    #: The plugin unique identifier.
    id = PKG + ".plugin"

    #: The plugin name (suitable for displaying to the user).
    name = "Dropbot Tools Menu Plugin"

    #### Contributions to extension points made by this plugin ################

    contributed_task_extensions = List(contributes_to=TASK_EXTENSIONS)

    #### Trait initializers ###################################################

    def _contributed_task_extensions_default(self):

        from .menus import dropbot_tools_menu_factory

        return [
            TaskExtension(
                task_id="device_viewer.task",
                actions=[
                    SchemaAddition(
                        factory=dropbot_tools_menu_factory,
                        before="TaskToggleGroup",
                        path='MenuBar/Tools',
                    )

                ]
            )
        ]