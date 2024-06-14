import time

import h5py
import json
from collections import OrderedDict
from ..utils.logger import initialize_logger

logger = initialize_logger(__name__)

protocol_data = OrderedDict([
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


def execute_step(step):
    description = step['Description']
    duration = step['Duration']
    voltage = step['Voltage']
    frequency = step['Frequency']

    print(f"Executing {description}: Duration={duration}s, Voltage={voltage}V, Frequency={frequency}Hz")
    time.sleep(duration)


def execute_protocol(protocol, order):
    steps_by_order = extract_commands(protocol)
    print(steps_by_order)

    for step_order in order:
        execute_step(steps_by_order[step_order-1])


# Save protocol data to an HDF5 file
protocol_filename = 'protocol.h5'
save_protocol_to_hdf5(protocol_data, protocol_filename)

# Load protocol data from the HDF5 file
protocol_data2 = load_protocol_from_hdf5(protocol_filename)
print(protocol_data2)

# Create execution order
execution_order = create_execution_order(protocol_data2)
print(execution_order)

# Execute the protocol
execute_protocol(protocol_data2, execution_order)
