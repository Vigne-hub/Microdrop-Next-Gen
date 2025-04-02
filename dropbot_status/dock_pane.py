# enthought imports
from pyface.tasks.dock_pane import DockPane

from .consts import PKG, PKG_name


class DropbotStatusDockPane(DockPane):
    """
    A dock pane to view the status of the dropbot.
    """
    #### 'ITaskPane' interface ################################################

    id = PKG + ".pane"
    name = f"{PKG_name} Dock Pane"

    def create_contents(self, parent):
        from .dramatiq_dropbot_status_controller import DramatiqDropbotStatusController
        from .widget import DropBotStatusWidget

        view = DropBotStatusWidget()
        view.setController(DramatiqDropbotStatusController)

        return view
