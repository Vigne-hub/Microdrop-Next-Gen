# enthought imports
from traits.api import Instance
from pyface.tasks.api import TaskPane
from pyface.qt.QtGui import QGraphicsScene
from pyface.qt.QtOpenGLWidgets import QOpenGLWidget
from pyface.qt.QtCore import Qt

# local imports
from .electrodes_view import ElectrodeLayer
from ..utils.auto_fit_graphics_view import AutoFitGraphicsView
from logger import get_logger

logger = get_logger(__name__)


class DeviceViewerPane(TaskPane):
    """
    A widget for viewing the device. This puts the electrode layer into a graphics view.
    """

    # ----------- Device View Pane traits ---------------------

    scene = Instance(QGraphicsScene)
    view = Instance(AutoFitGraphicsView)
    current_electrode_layer = Instance(ElectrodeLayer, allow_none=True)

    # --------- Device View trait initializers -------------
    def _scene_default(self):
        return QGraphicsScene()

    def _view_default(self):
        view = AutoFitGraphicsView(self.scene)
        view.setObjectName('device_view')
        view.setViewport(QOpenGLWidget())

        return view

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

    def set_new_layer_from_model(self, new_model):
        self.remove_current_layer()
        self.current_electrode_layer = ElectrodeLayer("layer1", new_model)
        self.scene.addItem(self.current_electrode_layer)

    def fit_scene_to_view(self):
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
