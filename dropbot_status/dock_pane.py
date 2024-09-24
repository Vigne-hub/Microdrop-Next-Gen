# enthought imports
from pyface.tasks.dock_pane import DockPane

# local imports
from dropbot_status.widget import DropBotControlWidget

from .consts import PKG


class DropbotStatusDockPane(DockPane):
    """
    A dock pane to set the voltage and frequency of the dropbot device.
    """
    #### 'ITaskPane' interface ################################################

    id = PKG + ".pane"
    name = "Dropbot Status Dock Pane"

    #### 'ManualControlsPane' interface ##########################################

    def create_contents(self, parent):
        return DropBotControlWidget()