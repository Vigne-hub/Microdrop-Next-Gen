# enthought imports
from pyface.tasks.dock_pane import DockPane

# local imports
from dropbot_status.widget import DropBotStatusWidget

from .consts import PKG


class DropbotStatusDockPane(DockPane):
    """
    A dock pane to view the status of the dropbot.
    """
    #### 'ITaskPane' interface ################################################

    id = PKG + ".pane"
    name = "Dropbot Status Dock Pane"

    def create_contents(self, parent):

        return DropBotStatusWidget()