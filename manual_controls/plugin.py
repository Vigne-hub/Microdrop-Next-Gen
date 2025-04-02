# enthought imports
from pyface.action.schema.schema_addition import SchemaAddition
from traits.api import List
from envisage.api import Plugin, TASK_EXTENSIONS
from envisage.ui.tasks.api import TaskExtension

from device_viewer.consts import PKG as device_viewer_PKG

from .consts import PKG, PKG_name


class ManualControlsPlugin(Plugin):
    """ Contributes UI actions on top of the IPython Kernel Plugin. """

    #### 'IPlugin' interface ##################################################

    #: The plugin unique identifier.
    id = PKG + ".plugin"

    #: The plugin name (suitable for displaying to the user).
    name = f"{PKG_name} Plugin"

    #### Contributions to extension points made by this plugin ################

    contributed_task_extensions = List(contributes_to=TASK_EXTENSIONS)

    #### Trait initializers ###################################################

    def _contributed_task_extensions_default(self):
        from .DockPane import ManualControlsDockPane
        from .menus import menu_factory

        return [
            TaskExtension(
                task_id=f"{device_viewer_PKG}.task",
                dock_pane_factories=[ManualControlsDockPane],
                actions=[
                    SchemaAddition(
                        factory=menu_factory,
                        before="TaskToggleGroup",
                        path='MenuBar/View',
                    )

                ]
            )
        ]
