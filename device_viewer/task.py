# system imports.
import json
from functools import partial
import os
import dramatiq

# Enthought library imports.
from pyface.tasks.action.api import SMenu, SMenuBar, TaskToggleGroup, TaskAction
from pyface.tasks.api import Task, TaskLayout, Tabbed
from pyface.api import FileDialog, OK
from traits.api import Instance, Str, provides

# Local imports.
from .models.electrodes import Electrodes
from .views.device_view_pane import DeviceViewerPane
from device_viewer.views.electrode_view.electrode_layer import ElectrodeLayer
from .consts import ELECTRODES_STATE_CHANGE

from microdrop_utils.dramatiq_pub_sub_helpers import publish_message
from microdrop_utils._logger import get_logger
from microdrop_utils.i_dramatiq_controller_base import IDramatiqControllerBase

logger = get_logger(__name__)
DEFAULT_SVG_FILE = f"{os.path.dirname(__file__)}{os.sep}2x3device.svg"


@provides(IDramatiqControllerBase)
class DeviceViewerTask(Task):

    #### 'IDramatuqControllerBase' interface #####
    listener = Instance(dramatiq.Actor)

    #### 'Task' interface #####################################################

    id = "device_viewer.task"
    name = "Device Viewer"

    menu_bar = SMenuBar(

        SMenu(
            TaskAction(id="open_svg_file", name='&Open SVG File', method='open_file_dialog', accelerator='Ctrl+O'),
            id="File", name="&File"
        ),

        SMenu(id="Edit", name="&Edit"),

        SMenu(id="Tools", name="&Tools"),

        SMenu(TaskToggleGroup(), id="View", name="&View")
    )

    def create_central_pane(self):
        """Create the central pane with the device viewer widget with a default view.
        """

        return DeviceViewerPane(electrodes=self.electrodes_model)

    def create_dock_panes(self):
        """Create any dock panes needed for the task."""
        return [
        ]

    def activated(self):
        """Called when the task is activated."""
        logger.debug(f"Device Viewer Task activated. Setting default view with {DEFAULT_SVG_FILE}...")
        _electrodes = Electrodes()
        _electrodes.set_electrodes_from_svg_file(DEFAULT_SVG_FILE)

        self.electrodes_model = _electrodes

    #### 'DeviceViewerTask' interface ##########################################

    electrodes_model = Instance(Electrodes)

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
        publish_message(topic=ELECTRODES_STATE_CHANGE, message=json.dumps(self.electrodes_model.channels_states_map))

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
    # UI Controller interface.
    ###########################################################################

    def __handle_electrode_layer_events(self):
        """Handle events from the panes. Any Notifications, Updates, etc. should be done here."""

        ################### Handler Method Connections ####################################

        for electrode_id, electrode_view in self.window.central_pane.current_electrode_layer.electrode_views.items():
            electrode_view.on_leftClicked = partial(
                self.on_electrode_leftClicked,  # handler method
                electrode_id, self.electrodes_model, self.window.central_pane.current_electrode_layer  # args
            )

    ################# Handler Methods ################################################

    # TODO: maybe make these methods set from services or a task extension.

    @staticmethod
    def on_electrode_leftClicked(_electrode_id: Str, _electrodes_model: Electrodes,
                                 _electrode_view_layer: ElectrodeLayer):
        """
        Handle the event when an electrode is clicked.

        params
        _electrode_id (str): Provide electrode id clicked by user.

        _electrodes_model (Electrodes): Provide all the electrodes available. Need this to check other models with same
                                        channel as the current electrode clicked

        _electrode_view_layer (ElectrodeLayer): Provide all electrodes view elements. Need to update all the ones affected
                                                by current click based on their channel.
        """

        logger.debug(f"Electrode {_electrode_id} clicked")

        # get electrode model for current electrode clicked
        _clicked_electrode_channel = _electrodes_model[_electrode_id].channel

        logger.debug(f"Channel {_clicked_electrode_channel} will be actuated")

        affected_electrode_ids = _electrodes_model.channels_electrode_ids_map[_clicked_electrode_channel]

        logger.debug(f"Affected electrodes {affected_electrode_ids} with same channel as clicked electrode")

        # NOTE: performance is ok, sticking to serial for loop. If need be, we may have to multithread.
        for affected_electrode_id in affected_electrode_ids:
            # obtain affected electrode object
            _electrode = _electrodes_model[affected_electrode_id]

            # update electrode model for electrode clicked and all electrodes with same channel affected by this click.
            _electrode.state = not _electrode.state

            # update electrode view for electrode clicked and all electrodes with same channel affected by this click.
            _electrode_view = _electrode_view_layer.electrode_views[affected_electrode_id]
            _electrode_view.update_color(_electrode.state)

        updated_channels_states_map = _electrodes_model.channels_states_map

        logger.info(f"New electrode channels states map: {updated_channels_states_map}")

        # publish event to all interested. Mainly to backend actors who need to know user has requested the electrode
        # to be actuated / unactuated.
        publish_message(topic=ELECTRODES_STATE_CHANGE, message=json.dumps(updated_channels_states_map))

    ##########################################################
    # 'IDramatiqControllerBase' interface.
    ##########################################################
    def traits_init(self):
        """
        This function needs to be here to let the listener be initialized to the default value automatically.
        We just do it manually here to make the code clearer.
        We can also do other initialization routines here if needed.

        This is equivalent to doing:

        def __init__(self, **traits):
            super().__init__(**traits)

        """
        logger.info("Starting DeviceViewer listener")
        self.listener = self._listener_default()

    def _listener_default(self) -> dramatiq.Actor:
        """
        Create a Dramatiq actor for listening to UI-related messages.

        Returns:
        dramatiq.Actor: The created Dramatiq actor.
        """

        @dramatiq.actor
        def device_viewer_listener(message, topic):
            """
            A Dramatiq actor that listens to messages.

            Parameters:
            message (str): The received message.
            topic (str): The topic of the message.

            """
            logger.info(f"DEVICE VIEWER LISTENER: Received message: {message} from topic: {topic}")

            topic = topic.split("/")
            method_name = f"_on_{topic[-1]}_triggered"
            # Check if the method exists and call it
            if hasattr(self, method_name) and getattr(self, method_name):
                # Use getattr to get the method and call it
                getattr(self, str(method_name))(message)

            else:
                logger.warning(f"Method for {topic[-1]} not found")

        return device_viewer_listener

    ####### handlers for dramatiq listener topics ##########
    def _on_setup_success_triggered(self, message):
        publish_message(topic=ELECTRODES_STATE_CHANGE, message=json.dumps(self.electrodes_model.channels_states_map))

    ##########################################################
    # Public interface.
    ##########################################################
    def show_help(self):
        """Show the help dialog."""
        logger.info("Showing help dialog.")


