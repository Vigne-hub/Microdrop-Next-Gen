from traits.api import Instance, List, Str, observe, File
from traitsui.api import View, UItem, HGroup, Item, EnumEditor
from pyface.tasks.api import TraitsTaskPane
from pyface.qt.QtWidgets import QWidget, QVBoxLayout

from .device_viewer_qt import DeviceViewerWidget  # Import your existing widget
import os

class DeviceViewerPane(TraitsTaskPane):
    #### 'ITaskPane' interface ################################################

    id = "envisage_sample.plugins.frontend.qt_widgets.device_viewer.pane"
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
