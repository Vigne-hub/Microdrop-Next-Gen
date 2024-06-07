# enthought imports
from traits.api import Instance, List, File
from traitsui.api import View, UItem
from pyface.tasks.api import TaskPane
from pyface.qt.QtWidgets import QWidget, QVBoxLayout

# Import your existing widget
from .qt.device_viewer_qt import DeviceViewerWidget


class DeviceViewerPane(TaskPane):
    #### 'ITaskPane' interface ################################################

    id = "qt_widgets.device_viewer.pane"
    name = "Device Viewer Pane"

    #### 'DeviceViewerPane' interface #########################################

    device_viewer_widget = Instance(DeviceViewerWidget)
    svg_files = List(File)
    selected_svg_file = File

    def create(self, parent):
        self.control = QWidget(parent)
        layout = QVBoxLayout(self.control)

        # Create an instance of your DeviceViewerWidget and add it to the layout
        if not self.device_viewer_widget:
            self.device_viewer_widget = DeviceViewerWidget()

        layout.addWidget(self.device_viewer_widget)

    view = View(
        UItem("device_viewer_widget", style="custom"),
        resizable=True,
    )
