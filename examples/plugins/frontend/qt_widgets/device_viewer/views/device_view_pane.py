# enthought imports
from traits.api import Str, Instance
from pyface.tasks.api import TaskPane
from pyface.qt.QtGui import QGraphicsScene
from pyface.qt.QtOpenGLWidgets import QOpenGLWidget
from pyface.qt.QtCore import Qt

# local imports
from .electrodes_view import ElectrodeLayer
from ..utils.auto_fit_graphics_view import AutoFitGraphicsView
from ... import initialize_logger

logger = initialize_logger(__name__)

# system imports
import os


class DeviceViewerPane(TaskPane):
    """
    A widget for viewing the device. This puts the electrode layer into a graphics view.
    """

    # ----------- Device View Pane traits ---------------------

    scene = Instance(QGraphicsScene)
    view = Instance(AutoFitGraphicsView)
    current_electrode_layer = Instance(ElectrodeLayer, allow_none=True)
    svg_file = Str()

    # --------- Device View trait initializers -------------
    def _scene_default(self):
        return QGraphicsScene()

    def _view_default(self):
        view = AutoFitGraphicsView(self.scene)
        view.setObjectName('device_view')
        view.setViewport(QOpenGLWidget())

        return view

    # ------- Device Veiw trait change handlers -----------------
    def _svg_file_changed(self, new_path):
        """
        Trigger an update to redraw and re-initialize the svg widget once a new svg file is selected.
        """
        self.current_electrode_layer = ElectrodeLayer("layer1", new_path)
        self.remove_current_layer()
        self.scene.addItem(self.current_electrode_layer)
        logger.debug(f"Layer {self.current_electrode_layer.id} added -> {new_path}")
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    # ------- Device View class methods -------------------------
    def remove_current_layer(self):
        """
        Utility methods to remove current scene's electrode layer.
        """
        if self.current_electrode_layer:
            self.scene.removeItem(self.current_electrode_layer)
            self.scene.clear()
            self.scene.update()

    # ITaskPane interface
    def create(self, parent):
        self.control = self.view
        self.control.setParent(parent)