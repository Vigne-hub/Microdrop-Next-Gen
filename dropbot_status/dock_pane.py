# enthought imports
from pyface.tasks.dock_pane import DockPane

# local imports
from .widget import DropBotStatusWidget

from .consts import PKG


class DropbotStatusDockPane(DockPane):
    """
    A dock pane to view the status of the dropbot.
    """
    #### 'ITaskPane' interface ################################################

    id = PKG + ".pane"
    name = "Dropbot Status Dock Pane"

    #### 'IDockPane' interface ################################################

    #: Make sure pane is currently detached from the main window.
    floating = True

    #: Make sure the pane is currently visible.
    visible = True

    def create_contents(self, parent):

        return DramatiqDropbotStatusWidget()