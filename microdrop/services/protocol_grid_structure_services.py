import json
import os
import time
from collections import OrderedDict

import h5py
from traits.api import Dict, Callable, Any, HasTraits, provides
from traits.trait_types import Str, List

from ..interfaces.i_protocol_grid_controller_service import IPGSService
from microdrop_utils._logger import get_logger

logger = get_logger(__name__)


@provides(IPGSService)
class ProtocolGridStructureService(HasTraits):
    id = "app.protocol_grid_structure_services"
    name = "Protocol Grid Structure Services"
    steps = List()
    electrodes_on = Dict(key_trait=Str(), value_trait=List(Str))
    file_save_dir = Str()
    file_name = Str()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.steps = []
        self.protocol_data = []
        self.electrodes_on = {}
        self.file_save_dir = f"{os.getcwd()}{os.sep}Protocol_Saves"
        self.file_name = ""

    def add_step(self, step: str, electrodes_on: list[str]):
        self.steps.append(step)
        self.electrodes_on[step] = electrodes_on

    @staticmethod
    def save_protocol_to_hdf5(protocol, filename):
        def save_step(group, step_name, step):
            step_group = group.create_group(step_name)
            for key, value in step.items():
                if isinstance(value, dict):
                    step_group.attrs[key] = json.dumps(value)
                    step_group.attrs[f"{key}_is_json"] = True  # Marker to indicate this attribute is a JSON string
                else:
                    step_group.attrs[key] = value

        with h5py.File(filename, 'w') as f:
            f.attrs['keys_order'] = list(protocol.keys())
            for key, value in protocol.items():
                if isinstance(value, dict) and "Order" in value:
                    save_step(f, key, value)
                elif isinstance(value, dict):
                    group = f.create_group(key)
                    group.attrs["Order"] = value.get("Order", 0)
                    for subkey, subvalue in value.items():
                        if subkey != "Order":
                            save_step(group, subkey, subvalue)
                else:
                    f.attrs[key] = value

    @staticmethod
    def load_protocol_from_hdf5(filename):
        protocol = OrderedDict()

        def load_step(group):
            step = {}
            for key in group.attrs.keys():
                if group.attrs.get(f"{key}_is_json", False):
                    step[key] = json.loads(group.attrs[key])
                else:
                    step[key] = group.attrs[key]
            return step

        with h5py.File(filename, 'r') as f:
            keys_order = f.attrs['keys_order']
            for key in keys_order:
                sub_group = f[key]
                if "Order" in sub_group.attrs:
                    protocol[key] = load_step(sub_group)
                else:
                    protocol[key] = OrderedDict()
                    for subkey in sub_group.keys():
                        protocol[key][subkey] = load_step(sub_group[subkey])
                    protocol[key]["Order"] = sub_group.attrs["Order"]

        return protocol

    @staticmethod
    def create_execution_order(protocol):
        order = []

        def collect_steps(protocol_dict):
            steps = []
            for key, value in protocol_dict.items():
                if isinstance(value, dict) and "Order" in value:
                    steps.append(value)
                elif isinstance(value, dict):
                    group_steps = {"Repetitions": value.get("Repetitions", 1)}
                    for subkey, subvalue in value.items():
                        if subkey != "Repetitions":
                            group_steps[subkey] = subvalue
                    steps.append(group_steps)
                else:
                    steps.append(value)
            return steps

        steps = collect_steps(protocol)
        for step in steps:
            if "Repetitions" in step:
                repetitions = step["Repetitions"]
                substeps = [value for key, value in step.items() if isinstance(value, dict) and "Order" in value]
                for _ in range(repetitions):
                    for substep in substeps:
                        order.append(substep["Order"])
            else:
                order.append(step["Order"])

        return order

    @staticmethod
    def extract_commands(protocol_data):
        commands = []
        for key, value in protocol_data.items():
            if 'Description' in value:  # This is a single step
                command = {k: v for k, v in value.items() if k != 'Order'}
                commands.append(command)
            else:  # This is a step group
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, dict) and 'Description' in sub_value:
                        command = {k: v for k, v in sub_value.items() if k != 'Order'}
                        commands.append(command)
        return commands

    @staticmethod
    def execute_step(step):
        description = step['Description']
        duration = step['Duration']
        voltage = step['Voltage']
        frequency = step['Frequency']

        logger.info(f"Executing {description}: Duration={duration}s, Voltage={voltage}V, Frequency={frequency}Hz")
        time.sleep(0)

    def execute_protocol(self, protocol, order):
        """ Execute the protocol based on the order list provided. """
        steps_by_order = self.extract_commands(protocol)  # gets list of unique command rows in the protocol
        logger.info(steps_by_order)

        for step_order in order:
            self.execute_step(steps_by_order[step_order - 1])  # execute the command based on the order

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


if __name__ == '__main__':
    example_protocol = OrderedDict([
        ("Step 1", {"Order": 1, "Description": "Monkas1", "Duration": 2, "Voltage": 15, "Frequency": 10000}),
        ("Step-Group[2-4]", {
            "Order": -1,
            "Repetitions": 5,
            "Step 2": {"Order": 2, "Description": "Monkas2", "Duration": 4, "Voltage": 25, "Frequency": 20000},
            "Step 3": {"Order": 3, "Description": "Monkas3", "Duration": 6, "Voltage": 35, "Frequency": 30000},
            "Step 4": {"Order": 4, "Description": "Monkas4", "Duration": 8, "Voltage": 45, "Frequency": 40000}
        }),
        ("Step 5", {"Order": 5, "Description": "Monkas5", "Duration": 10, "Voltage": 55, "Frequency": 50000})
    ])

    filename = "test_protocol.h5"
    ProtocolGridStructureService.save_protocol_to_hdf5(example_protocol, filename)
    protocol = ProtocolGridStructureService.load_protocol_from_hdf5(filename)
    order = ProtocolGridStructureService.create_execution_order(protocol)
    ProtocolGridStructureService().execute_protocol(protocol, order)

    
