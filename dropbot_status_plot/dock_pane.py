# enthought imports
from pyface.tasks.dock_pane import DockPane

from dropbot_status.dramatiq_dropbot_status_controller import DramatiqDropbotStatusController
from .consts import PKG, PKG_name


class DropbotStatusDockPane(DockPane):
    """
    A dock pane to view the status of the dropbot.
    """
    #### 'ITaskPane' interface ################################################

    id = PKG + ".pane"
    name = PKG_name + " Dock Pane"

    def create_contents(self, parent):
        from .widget import DropBotStatusPlotWidget

        view = DropBotStatusPlotWidget()

        # we can use the same controller as the basic dramatiq dropbot status plugin
        view.controller = DramatiqDropbotStatusController

        return view
