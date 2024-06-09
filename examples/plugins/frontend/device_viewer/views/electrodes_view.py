# library imports
import numpy as np

# local imports
from _logger import get_logger

# enthought imports
from pyface.qt.QtCore import Qt
from pyface.qt.QtGui import (QColor, QPen, QBrush, QFont, QPainterPath, QGraphicsPathItem, QGraphicsTextItem,
                             QGraphicsItem, QGraphicsItemGroup)

logger = get_logger(__name__, level='DEBUG')

default_colors = {True: '#8d99ae', False: '#0a2463', 'no-channel': '#fc8eac',
                  'droplet': '#06d6a0', 'line': '#3e92cc', 'connection': '#ffffff'}

default_alphas = {'line': 1.0, 'fill': 1.0, 'text': 1.0}


class ElectrodeView(QGraphicsPathItem):

    def __init__(self, id_, electrode, path_data, parent=None):
        super().__init__(parent)

        self.state_map = {k: v for k, v in default_colors.items()}
        self.state_map[None] = self.state_map[False]

        self.electrode = electrode
        self.id = id_
        self.alphas = default_alphas

        if str(self.electrode.channel) == 'None':
            self.state_map[False] = default_colors['no-channel']
            self.state_map[True] = default_colors['no-channel']
            self.state_map[None] = default_colors['no-channel']

        self.path = QPainterPath()
        self.path.moveTo(path_data[0][0], path_data[0][1])
        for x, y in path_data:
            self.path.lineTo(x, y)
        self.path.closeSubpath()
        self.setPath(self.path)

        # Pen for the outline
        self.pen_color = QColor(self.state_map['line'])
        self.pen_color.setAlphaF(self.alphas['line'])
        self.pen = QPen(self.pen_color, 1)  # line color outline
        self.setPen(self.pen)

        # Brush for the fill
        self.color = QColor(self.state_map[False])
        self.color.setAlphaF(self.alphas['fill'])
        self.brush = QBrush(self.color)  # Default fill color
        self.setBrush(self.brush)

        # Text item
        self.text_path = QGraphicsTextItem(parent=self)
        self.text_color = QColor(Qt.white)
        self.text_color.setAlphaF(self.alphas['text'])
        self.text_path.setDefaultTextColor(self.text_color)
        self.path_extremes = [np.min(path_data[:, 0]), np.max(path_data[:, 0]),
                              np.min(path_data[:, 1]), np.max(path_data[:, 1])]
        self.fit_text_in_path(str(self.electrode.channel), self.path_extremes)

        self.enable_electrode()

    def disable_electrode(self):
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, False)

    def enable_electrode(self):
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True)

    def mousePressEvent(self, event):
        self.on_clicked()
        super().mousePressEvent(event)  # Call the superclass method to ensure proper event handling

    def on_clicked(self):
        """
        Method to be implemented by Controller
        """
        pass

    def fit_text_in_path(self, text: str, path_extremes, default_font_size: int = 8):
        if text == 'None':
            self.text_path.setPlainText('')
            self.state_map[False] = default_colors['no-channel']
            self.state_map[True] = default_colors['no-channel']
            self.state_map[None] = default_colors['no-channel']
        else:
            self.text_path.setPlainText(text)
            self.state_map[False] = default_colors[False]
            self.state_map[True] = default_colors[True]
            self.state_map[None] = default_colors[False]
        # Determine the font size based on the path size
        left, right, top, bottom = path_extremes
        range_x = right - left
        range_y = bottom - top
        if len(text) == 1:
            font_size = min(range_x, range_y) / 1.2
        elif len(text) == 2:
            font_size = min(range_x, range_y) / 2
        else:
            font_size = min(range_x, range_y) / 3
            if font_size < default_font_size:
                font_size = default_font_size

        self.text_path.setFont(QFont('Arial', font_size))
        # Adjust the font size to fit the text in the path
        text_size = self.text_path.document().size()
        # center the text to the path
        posx = left + (right - left - text_size.width()) / 2
        posy = top + (bottom - top - text_size.height()) / 2
        self.text_path.setPos(posx, posy)

    def update_color(self, state):
        self.color = QColor(self.state_map.get(state, self.state_map[False]))
        self.color.setAlphaF(self.alphas['fill'])
        self.setBrush(QBrush(self.color))
        self.update()

    def update_alpha(self, line=False, fill=False, text=False, global_alpha=False):
        if line or global_alpha:
            self.pen_color.setAlphaF(self.alphas['line'])
            self.setPen(QPen(self.pen_color, 1))

        if fill or global_alpha:
            self.color.setAlphaF(self.alphas['fill'])
            self.setBrush(QBrush(self.color))

        if text or global_alpha:
            self.text_color.setAlphaF(self.alphas['text'])
            self.text_path.setDefaultTextColor(self.text_color)

        self.update()


class ElectrodeLayer(QGraphicsItemGroup):

    def __init__(self, id_: str, electrodes, parent=None):
        super().__init__(parent=parent)

        self.id = id_
        self.setHandlesChildEvents(False)  # Pass events to children

        self.electrode_views = {}

        svg = electrodes.svg_model

        # # Scale to approx 360p resolution for display
        modifier = max(640 / (svg.max_x - svg.min_x), 360 / (svg.max_y - svg.min_y))

        logger.debug(f"Creating Electrode Layer {id_} with {len(electrodes.electrodes)} electrodes.")

        for electrode_id, electrode in electrodes.electrodes.items():
            self.electrode_views[electrode_id] = ElectrodeView(electrode_id, electrodes[electrode_id],
                                                               modifier * electrode.path[:, 0, :])

            self.addToGroup(self.electrode_views[electrode_id])

        self._electrodes = electrodes

        self.connections = [con * modifier for con in svg.connections]
        self.connection_items = []
        self.draw_connections()

    def change_alphas(self, alpha: float, **kwargs):
        if kwargs.get('path'):
            self.update_connection_alpha(alpha)
            kwargs.pop('path')
        for name, e in self._electrodes.items():
            for k in kwargs.keys():
                if k in ['line', 'fill', 'text']:
                    self.electrode_views[name].alphas[k] = alpha
                if k == 'global_alpha':
                    self.electrode_views[name].alphas['line'] = alpha
                    self.electrode_views[name].alphas['fill'] = alpha
                    self.electrode_views[name].alphas['text'] = alpha

            self.electrode_views[name].update_alpha(**kwargs)

    def draw_connections(self):
        for connection in self.connections:
            path = QPainterPath()
            coords = connection.flatten()
            path.moveTo(coords[0], coords[1])
            path.lineTo(coords[2], coords[3])

            connection_item = QGraphicsPathItem(path, parent=self)
            color = QColor(default_colors['connection'])
            color.setAlphaF(1.0)
            connection_item.setPen(QPen(color, 1))
            self.connection_items.append(connection_item)

    def update_connection_alpha(self, alpha: float):
        for item in self.connection_items:
            color = item.pen().color()
            color.setAlphaF(alpha)
            item.setPen(QPen(color, 1))
            item.update()