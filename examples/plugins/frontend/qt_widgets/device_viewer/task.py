# Enthought library imports.
from pyface.tasks.action.api import SMenu, SMenuBar, TaskToggleGroup, TaskAction, TaskActionController
from pyface.tasks.api import Task, TaskLayout
from pyface.api import FileDialog, OK

# Local imports.
from .views.device_view_pane import DeviceViewerPane


class DeviceViewerTask(Task):
    #### 'Task' interface #####################################################

    id = "qt_widgets.device_viewer.task"
    name = "Device Viewer"

    menu_bar = SMenuBar(

        # File menu
        SMenu(
            TaskAction(
                id="open_svg_file",
                name='&Open SVG File',
                method='open_file_dialog',
                accelerator='Ctrl+O'),
            id="File",
            name="&File"),

        # View Menu
        SMenu(
            TaskToggleGroup(),
            id="View",
            name="&View")
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

    ###########################################################################
    # Menu actions.
    ###########################################################################

    def open_file_dialog(self):
        """Open a file dialog to select an SVG file and set it in the central pane."""
        dialog = FileDialog(action='open', wildcard='SVG Files (*.svg)|*.svg|All Files (*.*)|*.*')
        if dialog.open() == OK:
            svg_file = dialog.path
            self.window.central_pane.svg_file = svg_file