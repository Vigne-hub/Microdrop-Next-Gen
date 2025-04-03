# enthought imports
from traits.api import List
from envisage.api import Plugin, TASK_EXTENSIONS
from envisage.ui.tasks.api import TaskExtension

# microdrop imports
from message_router.consts import ACTOR_TOPIC_ROUTES
from microdrop_utils._logger import get_logger

# Initialize logger
logger = get_logger(__name__)

from .consts import PKG, PKG_name, ACTOR_TOPIC_DICT


class DropbotStatusPlotPlugin(Plugin):
    """ Contributes a dropbot status UI view with plots. """

    #### 'IPlugin' interface ##################################################

    #: The plugin unique identifier.
    id = PKG + ".plugin"
    #: The plugin name (suitable for displaying to the user).
    name = PKG_name + " Plugin"

    # This plugin contributes some actors that can be called using certain routing keys.
    actor_topic_routing = List([ACTOR_TOPIC_DICT], contributes_to=ACTOR_TOPIC_ROUTES)

    #### Contributions to extension points made by this plugin ################

    contributed_task_extensions = List(contributes_to=TASK_EXTENSIONS)

    #### Trait initializers ###################################################

    def _contributed_task_extensions_default(self):
        from .dock_panes import DropbotStatusCapacitancePlotDockPane, DropbotStatusVoltagePlotDockPane
        from device_viewer.consts import PKG

        return [
            TaskExtension(
                task_id=f"{PKG}.task",  # specify which task id it has to add on to
                dock_pane_factories=[
                    DropbotStatusVoltagePlotDockPane,
                    DropbotStatusCapacitancePlotDockPane
                ],
            )
        ]
