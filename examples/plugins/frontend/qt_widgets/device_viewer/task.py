# Enthought library imports.

from pyface.tasks.action.api import SMenu, SMenuBar, TaskToggleGroup
from pyface.tasks.api import Task, TaskLayout

# Local imports.
from .pane import DeviceViewerPane


class DeviceViewerTask(Task):
    #### 'Task' interface #####################################################

    id = "envisage_sample.plugins.frontend.qt_widgets.device_viewer.task"
    name = "Device Viewer"

    menu_bar = SMenuBar(
        SMenu(id="File", name="&File"),
        SMenu(id="Edit", name="&Edit"),
        SMenu(TaskToggleGroup(), id="View", name="&View"),
    )

    #### 'DeviceViewerTask' interface ##########################################

    # Any traits for this DeviceViewertask go here.

    ###########################################################################
    # 'Task' interface.
    ###########################################################################

    def create_central_pane(self):
        """Create the central pane with the device viewer widget. Keep`track of which device svg file is active so
        that dock panes can introspect it.
        """

        return DeviceViewerPane()

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
        )

    #### Trait change handlers ################################################

    # if any traits change handlers are needed, they go here.
