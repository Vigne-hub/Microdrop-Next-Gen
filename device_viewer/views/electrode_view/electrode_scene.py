from PySide6.QtWidgets import QGraphicsScene

from .electrode_view_helpers import get_mean_path, find_path_item
from .electrodes_view_base import ElectrodeView


class ElectrodeScene(QGraphicsScene):
    """
    Class to handle electrode view scene using elements contained in the electrode layer.
    Handles identifying mouse action across the scene.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.drag_start = None

    def mousePressEvent(self, event):
        """Handle the start of a drag operation."""
        item = self.itemAt(event.scenePos(), self.views()[0].transform())

        try:
            if isinstance(item.parentItem(), ElectrodeView):
                item = item.parentItem()
        except AttributeError:
            pass

        if isinstance(item, ElectrodeView):
            self.drag_start = item
            self.current_route = [item.electrode.channel]  # Start the route with this electrode
            self.route_points = [get_mean_path(item)]
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle the dragging motion."""
        if self.drag_start:

            # identify new item hovered over
            new_item = self.itemAt(event.scenePos(), self.views()[0].transform())

            # check if this item or parent item (if exists) is an electrode view
            try:
                if isinstance(new_item.parentItem(), ElectrodeView):
                    new_item = new_item.parentItem()
            except AttributeError:
                pass

            if isinstance(new_item, ElectrodeView):

                channel_ = new_item.electrode.channel
                if self.current_route[-1] != channel_:
                    self.current_route.append(channel_)

                    src = self.route_points[-1].flatten()
                    self.route_points.append(get_mean_path(new_item))
                    dst = self.route_points[-1].flatten()

                    # Define the query path: [(x1, y1), (x2, y2), ...]
                    query_path = [src, dst]  # MoveTo, LineTo

                    # Find the matching path item
                    found_item = find_path_item(self, query_path)
                    found_item.update_color()

                    print(f"path will be {'->'.join([str(i) for i in self.current_route])}")
                self.drag_start = new_item  # Update the drag start to the current electrode
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Finalize the drag operation."""
        print(self.current_route)
        self.drag_start = None
        self.current_route = []
        self.route_points = []
        super().mouseReleaseEvent(event)
