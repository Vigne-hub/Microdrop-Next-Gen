# library imports
import numpy as np

# local imports
from microdrop_utils._logger import get_logger

# enthought imports
from traits.api import Instance, Array, Str
from pyface.qt.QtCore import Qt
from pyface.qt.QtGui import (QColor, QPen, QBrush, QFont, QPainterPath, QGraphicsPathItem, QGraphicsTextItem,
                             QGraphicsItem, QGraphicsItemGroup)

from ..models.electrodes import Electrode

logger = get_logger(__name__, level='DEBUG')

default_colors = {True: '#8d99ae', False: '#0a2463', 'no-channel': '#fc8eac',
                  'droplet': '#06d6a0', 'line': '#3e92cc', 'connection': '#ffffff'}

default_alphas = {'line': 1.0, 'fill': 1.0, 'text': 1.0}


class ElectrodeView(QGraphicsPathItem):
    """
    Class defining the view for an electrode in the device viewer:

    - This view is a QGraphicsPathItem that represents the electrode as a polygon with a text label in the center.
    The view is responsible for updating the color and alpha of the electrode based on the state of the electrode.

    - The view also handles the mouse events for the electrode. The view is selectable and focusable.
    the callbacks for the clicking has to be implemented by a controller for the view.

    - The view requires an electrode model to be passed to it.
    """

    def __init__(self, id_: Str, electrode: Instance(Electrode), path_data: Array, parent=None):
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
        self._fit_text_in_path(str(self.electrode.channel), self.path_extremes)

        # Make the electrode selectable and focusable
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True)

    def mousePressEvent(self, event):
        # Check if left mouse button was clicked
        if event.button() == Qt.MouseButton.LeftButton:
            # Emit the rightClicked signal with arguments
            self.on_leftClicked()

        super().mousePressEvent(event)

    def on_leftClicked(self):
        """
        Method to be implemented by Controller. Whatever needs to be done on a click routine.
        """
        pass

    #################################################################################
    # electrode view protected methods
    ##################################################################################

    def _fit_text_in_path(self, text: str, path_extremes, default_font_size: int = 8):
        """
        Method to fit the text in the center of the electrode path
        """
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

    ##################################################################################
    # Public electrode view update methods
    ##################################################################################
    def update_color(self, state):
        """
        Method to update the color of the electrode based on the state
        """
        self.color = QColor(self.state_map.get(state, self.state_map[False]))
        self.color.setAlphaF(self.alphas['fill'])
        self.setBrush(QBrush(self.color))
        self.update()


class ElectrodeLayer(QGraphicsItemGroup):
    """
    Class defining the view for an electrode layer in the device viewer.

    - This view is a QGraphicsItemGroup that contains a group of electrode view objects
    - The view is responsible for updating the properties of all the electrode views contained in bulk.
    """

    def __init__(self, id_: str, electrodes, parent=None):
        super().__init__(parent=parent)

        self.id = id_
        self.setHandlesChildEvents(False)  # Pass events to children

        self.electrode_views = {}

        svg = electrodes.svg_model

        # # Scale to approx 360p resolution for display
        modifier = max(640 / (svg.max_x - svg.min_x), 360 / (svg.max_y - svg.min_y))

        logger.debug(f"Creating Electrode Layer {id_} with {len(electrodes.electrodes)} electrodes.")

        # Create the electrode views for each electrode from the electrodes model and add them to the group
        for electrode_id, electrode in electrodes.electrodes.items():
            self.electrode_views[electrode_id] = ElectrodeView(electrode_id, electrodes[electrode_id],
                                                               modifier * electrode.path[:, 0, :])

            self.addToGroup(self.electrode_views[electrode_id])

        # Create the connections between the electrodes
        self.connections = [con * modifier for con in svg.connections]
        # Create the connection items
        self.connection_items = []
        # Draw the connections
        self.draw_connections()

    def draw_connections(self):
        """
        Method to draw the connections between the electrodes in the layer
        """
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
