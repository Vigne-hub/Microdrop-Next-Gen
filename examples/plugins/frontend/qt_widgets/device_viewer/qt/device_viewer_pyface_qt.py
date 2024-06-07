# enthought imports
from pyface.qt.QtGui import QGraphicsScene
from pyface.qt.QtWidgets import QVBoxLayout, QPushButton, QApplication, QWidget
from traits.api import HasTraits, Instance, Str, observe, Property
from traitsui.api import View, UItem
from pyface.api import ApplicationWindow, FileDialog, OK

# system imports
import os
import logging

# local imports
from examples.plugins.frontend.qt_widgets.device_viewer.qt.electrodes_view import ElectrodeLayer
from examples.plugins.frontend.qt_widgets.device_viewer.utils.auto_fit_graphics_view import AutoFitGraphicsViewEditor, \
    AutoFitGraphicsView

logger = logging.getLogger(__name__)


class DeviceViewerWidget(HasTraits):
    """
    A widget for viewing the device
    """

    scene = Instance(QGraphicsScene)
    svg_path = Str
    svg_path_button = Instance(QPushButton)
    view = Instance(AutoFitGraphicsView)
    current_electrode_layer = Instance(ElectrodeLayer, allow_none=True)

    def _scene_default(self):
        return QGraphicsScene()

    def _svg_path_button_default(self):
        button = QPushButton('Select SVG File')
        button.clicked.connect(self.open_file_dialog)
        return button

    def _view_default(self):
        view = AutoFitGraphicsView(self.scene)
        view.setObjectName('device_view')
        return view

    def open_file_dialog(self):
        dialog = FileDialog(action='open', wildcard='SVG Files (*.svg)|*.svg|All Files (*.*)|*.*')
        if dialog.open() == OK:
            self.svg_path = dialog.path

    def _svg_path_changed(self, new_path):
        """
        Trigger an update to redraw and re-initialize the svg widget once a new svg file is selected.
        """

        # update the text of the button to show the name of the selected file
        self.svg_path_button.setText(os.path.basename(new_path))

        # obtain the new electrode layer
        self.current_electrode_layer = ElectrodeLayer("layer1", new_path)

        # remove the current layer and add the new
        self.remove_current_layer()
        self.scene.addItem(self.current_electrode_layer)

        logger.debug(f"Layer {self.current_electrode_layer.id} added -> {new_path}")

        # trigger a manual resize event to fit the scene rect: this is  a hack to get it to work properly
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.view.resize(self.view.width() + 1, self.view.height() + 1)

    def remove_current_layer(self):
        if self.current_electrode_layer:
            self.scene.removeItem(self.current_electrode_layer)
            logger.debug("Removed current electrode layer")
            self.scene.clear()
            self.scene.update()

    traits_view = View(
        UItem('view', editor=AutoFitGraphicsViewEditor(), style='custom'),
        UItem('svg_path_button', style='custom'),
        resizable=True
    )


class DeviceViewerWindow(ApplicationWindow):
    viewer = Instance(DeviceViewerWidget)

    def _viewer_default(self):
        return DeviceViewerWidget()

    def _create_contents(self, parent):
        main_widget = QWidget(parent)
        layout = QVBoxLayout(main_widget)
        layout.addWidget(self.viewer.view)
        layout.addWidget(self.viewer.svg_path_button)
        return main_widget


if __name__ == "__main__":
    import sys

    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

    window = DeviceViewerWindow()
    window.open()
    sys.exit(app.exec())
