from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGraphicsScene

from .electrode_view_helpers import find_path_item
from .electrodes_view_base import ElectrodeView
from microdrop_utils._logger import get_logger

logger = get_logger(__name__)


class ElectrodeScene(QGraphicsScene):
    """
    Class to handle electrode view scene using elements contained in the electrode layer.
    Handles identifying mouse action across the scene.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.electrode_pressed = None
        self.electrode_channels_visited = []
        self.electrode_ids_visited = []
        self._interaction_service = None

    @property
    def interaction_service(self):
        #: The service handling electrode interactions
        return self._interaction_service

    @interaction_service.setter
    def interaction_service(self, interaction_service):
        self._interaction_service = interaction_service

    def mousePressEvent(self, event):
        """Handle the start of a mouse click event."""

        if event.button() == Qt.LeftButton:
            self.mouseLeftClickEvent(event)

            super().mousePressEvent(event)

    def mouseLeftClickEvent(self, event):
        # Get the item under the mouse click using the scene's coordinates.
        item = self.itemAt(event.scenePos(), self.views()[0].transform())

        # Try to get the parent electrode view if available
        parent = getattr(item, "parentItem", lambda: None)()

        # Determine the electrode view: either the parent or the item itself.
        if isinstance(parent, ElectrodeView):
            electrode_view = parent
        elif isinstance(item, ElectrodeView):
            electrode_view = item
        else:
            # Neither the item nor its parent is an ElectrodeView, so exit.
            return

        # Record the clicked electrode view and initialize route tracking.
        self.electrode_pressed = electrode_view

        # Track the visited electrode IDs and channels.
        self.electrode_channels_visited = [electrode_view.electrode.channel]
        self.electrode_ids_visited = [electrode_view.id]

    def mouseMoveEvent(self, event):
        """Handle the dragging motion."""
        if self.electrode_pressed:
            # Identify the new item under the mouse cursor using the scene's transform.
            new_item = self.itemAt(event.scenePos(), self.views()[0].transform())

            # Safely attempt to get the parent of the new item if it exists.
            parent = getattr(new_item, "parentItem", lambda: None)()

            # Determine which item to use: prefer the parent if it's an ElectrodeView,
            # otherwise use the new_item itself if it's an ElectrodeView.
            if isinstance(parent, ElectrodeView):
                electrode_view = parent
            elif isinstance(new_item, ElectrodeView):
                electrode_view = new_item
            else:
                electrode_view = None

            # Only proceed if we have a valid electrode view.
            if electrode_view:
                channel_ = electrode_view.electrode.channel

                # Check if this channel differs from the last visited channel.
                if self.electrode_channels_visited[-1] != channel_:
                    # Append new channel and electrode ID to their respective lists.
                    self.electrode_channels_visited.append(channel_)
                    self.electrode_ids_visited.append(electrode_view.id)

                    # Determine the key for path lookup based on the last two visited electrodes.
                    src_key = self.electrode_ids_visited[-2]
                    dst_key = self.electrode_ids_visited[-1]
                    key = (src_key, dst_key)

                    # Find the corresponding path item and update its visual representation.
                    found_item = find_path_item(self, key)
                    found_item.update_color()

                    print(f"path will be {'->'.join(str(i) for i in self.electrode_channels_visited)}")

                # Update the electrode pressed to the current electrode view.
                self.electrode_pressed = electrode_view

        # Call the base class mouseMoveEvent to ensure normal processing continues.
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Finalize the drag operation."""

        # If it's a click (not a drag) since only one electrode selected:
        if len(self.electrode_channels_visited) == 1:
            if self.interaction_service:
                self.interaction_service.handle_electrode_click(self.electrode_ids_visited[0])

        else:
            # logger.info(self.electrode_channels_visited)
            pass

        self.electrode_pressed = None
        self.electrode_channels_visited = []
        super().mouseReleaseEvent(event)
