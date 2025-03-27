import numpy as np
from PySide6.QtGui import QColor, QPainterPath, QPen

from .electrodes_view_base import ElectrodeConnectionItem


def find_path_item(scene, path_data):
    """Find a QGraphicsPathItem with the exact path sequence"""
    for item in scene.items():
        if isinstance(item, ElectrodeConnectionItem):
            path = item.path()

            match = True
            for i, (expected_x, expected_y) in enumerate(path_data):
                element = path.elementAt(i)
                if not (abs(element.x - expected_x) < 0.1 and abs(element.y - expected_y) < 0.1):
                    match = False
                    break  # If any element doesn't match, break early

            if match:
                return item  # Found a matching path item

    return None  # No match found


def generate_connection_line(src: tuple, dst: tuple, color: QColor = None):
    """
    Paints a line based on src and dst coordinates.
    """
    path = QPainterPath()
    path.moveTo(src[0], src[1])
    path.lineTo(dst[0], dst[1])
    connection_item = ElectrodeConnectionItem(path)

    if color is not None:
        connection_item.setPen(QPen(color, 1))
    return connection_item


def get_mean_path(item):
    return np.mean(item.electrode.path, axis=0)
