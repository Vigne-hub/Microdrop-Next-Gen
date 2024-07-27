# enthought imports
from pyface.tasks.dock_pane import DockPane

# local imports
from microdrop.plugins.frontend_plugins.protocol_grid_controller.protocol_grid_controller_widget import PGCWidget

# This module's package.
PKG = '.'.join(__name__.split('.')[:-1])


class PGCDockPane(DockPane):
    """
    A dock pane to set the voltage and frequency of the dropbot device.
    """
    #### 'ITaskPane' interface ################################################

    id = PKG + ".pgc_widget"
    name = "Protocol Grid Controller"

    #### 'ManualControlsPane' interface ##########################################

    def create_contents(self, parent):
        return PGCWidget()
