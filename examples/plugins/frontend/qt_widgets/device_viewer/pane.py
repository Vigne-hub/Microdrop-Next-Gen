# enthought imports
from traits.api import Instance
from pyface.tasks.api import TaskPane
from pyface.qt.QtWidgets import QWidget, QVBoxLayout

# local imports
from .views.device_viewer_pyface_qt import DeviceViewerWidget


class DeviceViewerPane(TaskPane):

    # traits
    viewer = Instance(DeviceViewerWidget)

    # traits interface
    def _viewer_default(self):
        return DeviceViewerWidget()

    # ITaskPane interface
    def create(self, parent):
        self.control = QWidget(parent)
        layout = QVBoxLayout()
        layout.addWidget(self.viewer.view)
        layout.addWidget(self.viewer.svg_path_button)
        self.control.setLayout(layout)
