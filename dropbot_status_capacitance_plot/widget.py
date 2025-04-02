import json

from microdrop_utils.base_dropbot_status_plot_qwidget import BaseDropBotStatusPlotWidget


class DropBotStatusCapacitancePlotWidget(BaseDropBotStatusPlotWidget):
    """Widget for displaying real-time voltage data."""

    def __init__(self, *args, **kwargs):
        super().__init__(value_tracked_name="capacitance", value_tracked_unit="pF")

    ###################################################################################################################
    # Subscriber methods
    ###################################################################################################################

    ######################################### Handler methods #############################################

    ################# Capacitance Voltage readings ##################
    def _on_capacitance_updated_triggered(self, body):
        data = json.loads(body)
        capacitance = data.get('capacitance', '0 pF')

        # Update capacitance plot
        self.update_tracked_value(capacitance)