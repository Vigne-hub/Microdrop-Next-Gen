# system imports.
from functools import partial
import os

# Enthought library imports.
from pyface.tasks.action.api import SMenu, SMenuBar, TaskToggleGroup, TaskAction
from pyface.tasks.api import Task, TaskLayout, Tabbed
from pyface.api import FileDialog, OK
from traits.api import Instance

# Local imports.
from .models.electrodes import Electrodes, Electrode
from .views.device_view_pane import DeviceViewerPane
from microdrop_utils._logger import get_logger
from .views.electrodes_view import ElectrodeView

logger = get_logger(__name__)
DEFAULT_SVG_FILE = os.path.dirname(__file__) + "\\2x3device.svg"


class DeviceViewerTask(Task):
    #### 'Task' interface #####################################################

    id = "device_viewer.task"
    name = "Device Viewer"

    menu_bar = SMenuBar(

        # File menu
        SMenu(
            TaskAction(
                id="open_svg_file",
                name='&Open SVG File',
                method='open_file_dialog',
                accelerator='Ctrl+O'),
            id="File",
            name="&File"),

        # View Menu
        SMenu(
            TaskToggleGroup(),
            id="View",
            name="&View")
    )

    #### 'DeviceViewerTask' interface ##########################################

    electrodes_model = Instance(Electrodes)

    ###########################################################################
    # 'Task' interface.
    ###########################################################################

    def create_central_pane(self):
        """Create the central pane with the device viewer widget with a default view.
        """

        return DeviceViewerPane(electrodes=self.electrodes_model)

    def create_dock_panes(self):
        """Create any dock panes needed for the task."""
        return [
        ]

    ###########################################################################
    # Protected interface.
    ###########################################################################

    # ------------------ Trait initializers ---------------------------------

    def _default_layout_default(self):
        return TaskLayout(
            left=Tabbed(
            )

        )

    # --------------- Trait change handlers ----------------------------------------------

    def _electrodes_model_changed(self, new_model):
        """Handle when the electrodes model changes."""

        # Trigger an update to redraw and re-initialize the svg widget once a new svg file is selected.
        self.window.central_pane.set_view_from_model(new_model)
        logger.debug(f"New Electrode Layer added --> {new_model.svg_model.filename}")

        # setup event handlers for the new electrode layer
        self.__handle_electrode_layer_events()
        logger.debug(f"setting up handlers for new layer for new electrodes model {new_model}")

    ###########################################################################
    # Menu actions.
    ###########################################################################

    def open_file_dialog(self):
        """Open a file dialog to select an SVG file and set it in the central pane."""
        dialog = FileDialog(action='open', wildcard='SVG Files (*.svg)|*.svg|All Files (*.*)|*.*')
        if dialog.open() == OK:
            svg_file = dialog.path
            logger.info(f"Selected SVG file: {svg_file}")

            new_model = Electrodes()
            new_model.set_electrodes_from_svg_file(svg_file)
            logger.debug(f"Created electrodes from SVG file: {new_model.svg_model.filename}")

            self.electrodes_model = new_model
            logger.info(f"Electrodes model set to {new_model}")

    ###########################################################################
    # Controller interface.
    ###########################################################################

    def __handle_electrode_layer_events(self):
        """Handle events from the panes. Any Notifications, Updates, etc. should be done here."""

        ################### Handler Method Connections ####################################

        for electrode_id, electrode_view in self.window.central_pane.current_electrode_layer.electrode_views.items():

            electrode_view.on_clicked = partial(
                self.on_electrode_clicked, # handler method
                self.electrodes_model[electrode_id], electrode_view # args
            )

    ################# Handler Methods ################################################

    # TODO: need to make these methods set from services or a task extension if granular control needed.

    @staticmethod
    def on_electrode_clicked(_model: Electrode, _electrode_view: ElectrodeView):
        """Handle the event when an electrode is clicked."""

        logger.debug(f"Electrode {_model} clicked")

        # update the model
        _model.state = not _model.state

        # update the view
        _electrode_view.update_color(_electrode_view.electrode.state)

        # Do some other notification or updates or action here...

    def activated(self):
        """Called when the task is activated."""
        logger.debug(f"Device Viewer Task activated. Setting default view with {DEFAULT_SVG_FILE}...")
        _electrodes = Electrodes()
        _electrodes.set_electrodes_from_svg_file(DEFAULT_SVG_FILE)

        self.electrodes_model = _electrodes

    ##########################################################
    # Public interface.
    ##########################################################
    def show_help(self):
        """Show the help dialog."""
        logger.info("Showing help dialog.")

