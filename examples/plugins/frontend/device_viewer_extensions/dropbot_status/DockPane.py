# enthought imports
from pyface.tasks.dock_pane import DockPane

# local imports

from microdrop.plugins.frontend_plugins.dropbot_status.dropbot_status_widget import DropBotControlWidget

# This module's package.
PKG = '.'.join(__name__.split('.')[:-1])


class DropbotStatusDockPane(DockPane):
    """
    A dock pane to set the voltage and frequency of the dropbot device.
    """
    #### 'ITaskPane' interface ################################################

    id = PKG + ".dropbot_status"
    name = "Dropbot Status Dock Pane"

    #### 'ManualControlsPane' interface ##########################################

    def create_contents(self, parent):
        return DropBotControlWidget()