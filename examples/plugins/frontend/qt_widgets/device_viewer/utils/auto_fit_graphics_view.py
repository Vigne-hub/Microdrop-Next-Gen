from pyface.qt.QtWidgets import QGraphicsView
from pyface.qt.QtCore import Qt
from traitsui.basic_editor_factory import BasicEditorFactory
from traitsui.qt.editor import Editor

from ... import initialize_logger

logger = initialize_logger(__name__)


class AutoFitGraphicsView(QGraphicsView):
    """
    A QGraphicsView that automatically fits the scene rect when the view is resized
    """
    def resizeEvent(self, event):
        logger.debug(f"Resizing view size: {self.scene().sceneRect()}")
        self.fitInView(self.scene().sceneRect().adjusted(20, 20, 20, 20), Qt.AspectRatioMode.KeepAspectRatio)
        super().resizeEvent(event)


class _AutoFitGraphicsViewEditor(Editor):
    """
    Editor for AutoFitGraphicsView
    """
    def init(self, parent):
        self.control = AutoFitGraphicsView(parent)
        self.control.setObjectName('device_view')
        self.value = self.control  # Set the value of the editor to be the QGraphicsView instance
        self.set_frame_active(False)


class AutoFitGraphicsViewEditor(BasicEditorFactory):
    """
    BasicEditorFactory for AutoFitGraphicsView
    """
    klass = _AutoFitGraphicsViewEditor
