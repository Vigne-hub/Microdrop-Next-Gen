# Enthought library imports.
import os

from pyface.tasks.action.api import SMenu, SMenuBar, TaskToggleGroup
from pyface.tasks.api import PaneItem, Tabbed, Task, TaskLayout
from traits.api import adapt, Any, Instance, List
from traits.trait_types import File

# Local imports.
from .pane import DeviceViewerPane

class DeviceViewerTask(Task):
    #### 'Task' interface #####################################################

    id = "qt_widgets.device_viewer.task"
    name = "Device Viewer"

    menu_bar = SMenuBar(
        SMenu(id="File", name="&File"),
        SMenu(id="Edit", name="&Edit"),
        SMenu(TaskToggleGroup(), id="View", name="&View"),
    )

    #### 'DeviceViewerTask' interface ##########################################

    # The current path for the device viewer svg model.
    selected_svg_path = File

    ###########################################################################
    # 'Task' interface.
    ###########################################################################

    def create_central_pane(self):
        """Create the central pane with the device viewer widget. Keep`track of which device svg file is active so
        that dock panes can introspect it.
        """

        pane = DeviceViewerPane(selected_svg_file=f"device_svg_files{os.sep}2x3device.svg")

        self.selected_svg_path = pane.selected_svg_file

        return pane

    def create_dock_panes(self):
        """Create any dock panes needed for the task."""
        return [
        ]

    ###########################################################################
    # Protected interface.
    ###########################################################################

    #### Trait initializers ###################################################

    def _default_layout_default(self):
        return TaskLayout(
            left=Tabbed(
            )
        )

        #### Trait change handlers ################################################