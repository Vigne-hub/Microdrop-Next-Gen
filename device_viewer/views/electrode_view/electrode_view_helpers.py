import numpy as np
from PySide6.QtGui import QColor, QPainterPath, QPen

from .electrodes_view_base import ElectrodeConnectionItem


def find_path_item(scene, connected_electrodes_keys):
    """Find a QGraphicsPathItem with the exact path sequence"""
    for item in scene.items():
        if isinstance(item, ElectrodeConnectionItem):
            if item.key[0] in connected_electrodes_keys and item.key[1] in connected_electrodes_keys:
                return item

    return None  # No match found


def generate_connection_line(key, src: tuple, dst: tuple, color: QColor = None):
    """
    Paints a line based on src and dst coordinates.
    """
    path = QPainterPath()
    path.moveTo(src[0], src[1])
    path.lineTo(dst[0], dst[1])
    connection_item = ElectrodeConnectionItem(key, path)

    if color is not None:
        connection_item.setPen(QPen(color, 1))
    return connection_item


def get_mean_path(item):
    return np.mean(item.electrode.path, axis=0)
