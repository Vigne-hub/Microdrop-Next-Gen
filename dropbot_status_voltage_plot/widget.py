import json

from microdrop_utils.base_dropbot_status_plot_qwidget import BaseDropBotStatusPlotWidget


class DropBotStatusVoltagePlotWidget(BaseDropBotStatusPlotWidget):
    """Widget for displaying real-time voltage data."""

    def __init__(self):
        super().__init__(value_tracked_name="voltage", value_tracked_unit="V")

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
        self.update_tracked_value(voltage)