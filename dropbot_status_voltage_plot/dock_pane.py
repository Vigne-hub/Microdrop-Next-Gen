# enthought imports
from pyface.tasks.dock_pane import DockPane

from dropbot_status.dramatiq_dropbot_status_controller import DramatiqDropbotStatusController
from .consts import PKG, PKG_name


# Set the listener actor name based on the root module of the widget's class
listener_name = PKG + "_listener"


class DropbotStatusVoltagePlotDockPane(DockPane):
    """
    A dock pane to view the status of the dropbot.
    """
    #### 'ITaskPane' interface ################################################

    id = PKG + ".pane"
    name = PKG_name + " Voltage Dock Pane"

    def create_contents(self, parent):

        from .widget import DropBotStatusVoltagePlotWidget
        view = DropBotStatusVoltagePlotWidget()

        # we can use the same controller as the basic dramatiq dropbot status plugin
        view.controller = DramatiqDropbotStatusController

        return view