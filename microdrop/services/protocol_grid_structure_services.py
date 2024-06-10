import json
import os
from pathlib import Path

from traits.api import Dict, Callable, Any, HasTraits, provides
from traits.trait_types import Str, List

from ..interfaces.protocol_grid_structure_interface import IPGSService
from ..utils.logger import initialize_logger

logger = initialize_logger(__name__)


@provides(IPGSService)
class ProtocolGridStructureService(HasTraits):
    id = "app.protocol_grid_structure_services"
    name = "Protocol Grid Structure Services"
    steps = List()
    electrodes_on = Dict(key_trait=Str(), value_trait=List(Str))
    file_save_dir = Str()
    file_name = Str()

    def __init__(self, pub_sub_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.steps = []
        self.protocol_data = {}
        self.electrodes_on = {}
        self.file_save_dir = f"{os.getcwd()}{os.sep}Protocol_Saves"
        self.file_name = ""
        self.pub_sub_manager = pub_sub_manager
        self.create_device_view_update_publisher()
        self.create_protocol_view_update_publisher()

    def add_step(self, step: str, electrodes_on: list[str]):
        self.steps.append(step)
        self.electrodes_on[step] = electrodes_on

    def save_protocol(self, file_name):
        data_to_save = [self.protocol_data, self.electrodes_on]
        data_json = json.dumps(data_to_save)
        self.save_to_file(data_json, file_name)

    def load_protocol(self, file_path):
        self.file_name = file_path
        if file_path == "":
            return

        with open(file_path, "r") as protocol_file:
            table_data_json = protocol_file.read()

        # Publish the JSON data to the load_queue
        self.pub_sub_manager.publish(table_data_json, "update_protocol_view_signal")

        logger.info("Protocol loaded and published to load_queue")

    def save_to_file(self, table_data_json, file_name):
        if self.file_name is "":
            self.file_name = file_name

        save_file = f"{self.file_save_dir}{os.sep}{self.file_name}".removesuffix(".json")
        logger.info(f"Saving protocol to file: {save_file}.json")

        if os.path.exists(f"{save_file}.json"):
            logger.info("File already exists")
            logger.info("Overwriting file")

        else:
            logger.info("File does not exist")
            Path(save_file).parent.mkdir(parents=True, exist_ok=True)
            logger.info(f"File: {self.file_save_dir}{os.sep}{self.file_name} created")

        with open(f"{self.file_save_dir}{os.sep}{self.file_name}", "w") as protocol_file:
            protocol_file.write(table_data_json)
            logger.info("Protocol saved to file")

    def on_cell_changed(self, args):
        """
        Callback function on message received to update the structure snapshot of the
        current protocol grid controller. This is only for view data storing not for electrodes.
        """
        temp_protocol_data = args[0]  # gives it in proper dictionary string json format
        temp_protocol_data = json.loads(temp_protocol_data)

        """
        example:
        '{
        1: {"Description": "this is description 1", "Duration": 30, "Voltage": 100, "Frequency": 10000}, 
        2: {"Description": "this is description 2", "Duration": 20, "Voltage": 50, "Frequency": 10000},
        3: {"Description": "this is description 3", "Duration": 10, "Voltage": 60, "Frequency": 10000},
        }'
        
        json.loads turns it to dictionary
        """

        for key, value in temp_protocol_data.items():
            self.protocol_data[key] = value

    def on_electrode_clicked(self, args, kwargs):
        """
        Callback function on message received to update the electrodes_on snapshot of the
        current protocol grid controller. This is only for electrodes storing not for view data.

        should give data in form b'[int, int, int]'
        """
        steps_highlighted = kwargs["steps"]  # list
        electrodes_on = kwargs["electrodes"]  # list

        for step in steps_highlighted:
            self.electrodes_on[step] = electrodes_on

        # decide with vignesh whether on click when highlighting multiple rows if it should add
        # the electrode on state to each row or to the last row

    def publish_electrodes_active_to_device_view(self, kwargs):
        active_rows = kwargs["active rows"] # list of row numbers as strings
        message_electrode_list = []

        for row in active_rows:
            message_electrode_list.extend(self.electrodes_on[row])

        message_json = json.dumps(message_electrode_list)
        self.pub_sub_manager.publish(message_json, "update_device_view_signal")

    def create_device_view_update_publisher(self):
        self.pub_sub_manager.create_publisher("update_device_view_signal", "to_device_view")

    def create_protocol_view_update_publisher(self):
        self.pub_sub_manager.create_publisher("update_protocol_view_signal", "to_protocol_view")

