import json
import time
import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QTimer, Qt
from microdrop_utils._logger import get_logger
from microdrop_utils.base_dropbot_qwidget import BaseControllableDropBotQWidget

logger = get_logger(__name__)


class DropBotStatusPlotWidget(BaseControllableDropBotQWidget):
    """Widget for displaying real-time voltage data."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_ui()

    def init_ui(self):
        """Initialize the UI components."""
        # Create main layout
        self.layout = QVBoxLayout()

        # Create plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#2b2b2b')
        self.plot_widget.setTitle("Real-time Voltage Monitoring", color='w')
        self.plot_widget.setLabel('left', 'Voltage (V)', color='w')
        self.plot_widget.setLabel('bottom', 'Time (s)', color='w')

        # Enable mouse interaction for zooming and panning
        self.plot_widget.setMouseEnabled(x=True, y=True)

        # Configure Y-axis with major ticks every 50V
        y_axis = self.plot_widget.getAxis('left')
        y_axis.setTickSpacing(major=50, minor=10)
        y_axis.setStyle(tickTextOffset=5)

        # Add grid lines
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.getAxis('left').setTextPen('w')
        self.plot_widget.getAxis('bottom').setTextPen('w')

        # Create voltage curve with thicker line
        self.voltage_curve = self.plot_widget.plot(pen=pg.mkPen(color='y', width=2))

        # Add horizontal reference lines at key voltage levels
        self.plot_widget.addLine(y=0, pen=pg.mkPen(color='r', style=Qt.DashLine))
        self.plot_widget.addLine(y=50, pen=pg.mkPen(color='r', style=Qt.DashLine))
        self.plot_widget.addLine(y=100, pen=pg.mkPen(color='r', style=Qt.DashLine))
        self.plot_widget.addLine(y=150, pen=pg.mkPen(color='r', style=Qt.DashLine))

        # Add legend
        self.plot_widget.addLegend()
        # self.voltage_curve.setName('Voltage')

        self.layout.addWidget(self.plot_widget)

        # Data storage
        self.times = []
        self.voltages = []
        self.start_time = time.time()

        # Update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(100)  # Update every 100ms

        self.setLayout(self.layout)

    #### Update UI elements methods ###########

    def update_voltage(self, voltage_str):
        """Update the voltage reading."""
        try:
            # Extract numeric value from voltage string (e.g., "10.5 V" -> 10.5)
            voltage = float(voltage_str.split()[0])
            self.voltages.append(voltage)

            # Keep only last 100 seconds of data
            if len(self.voltages) > 1000:  # 100 seconds at 10Hz
                self.voltages.pop(0)

        except (ValueError, IndexError) as e:
            logger.error(f"Error parsing voltage value: {e}")

    def update_plot(self):
        """Update the plot with current data."""
        if not self.voltages:
            return

        current_time = time.time() - self.start_time
        self.times.append(current_time)

        # Keep time array in sync with voltage array
        if len(self.times) > len(self.voltages):
            self.times.pop(0)

        self.voltage_curve.setData(self.times, self.voltages)

    ###################################################################################################################
    # Subscriber methods
    ###################################################################################################################

    ######################################### Handler methods #############################################

    ################# Capacitance Voltage readings ##################
    def _on_capacitance_updated_triggered(self, body):
        data = json.loads(body)
        capacitance = data.get('capacitance', '0 pF')
        voltage = data.get('voltage', '0 V')

        # Update voltage plot
        self.update_voltage(voltage)
