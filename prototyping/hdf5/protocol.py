from collections import OrderedDict

import h5py
import numpy as np

# Example data
Protocol_data = OrderedDict([
    ('Protocol Name', 'Example_Protocol'),
    ('Step 1', [1, 2, 3, 4]),
    ('Step-Group[2-4]', {
        'Repetitions': 4,
        'Step 2': [5, 6, 7, 8],
        'Step 3': [9, 10, 11, 12],
        'Step 4': [13, 14, 15, 16]
    }),
    ('Step 5', [17, 18, 19, 20]),
    ('Step 6', [21, 22, 23, 24])
])


def save_protocol(data):
    def save_data(group, s_data):
        for key, value in s_data.items():
            if isinstance(value, dict):  # Nested group
                sub_group = group.create_group(key)
                if 'Repetitions' in value:
                    sub_group.attrs['Repetitions'] = value['Repetitions']
                save_data(sub_group, value)
            else:  # Dataset
                group.create_dataset(key, data=np.array(value))

    # Create an HDF5 file
    with h5py.File('protocol_data.h5', 'w') as file:
        protocol_name = data['Protocol Name']
        protocol_group = file.create_group(protocol_name)

        # Save data
        for key, value in data.items():
            if key != 'Protocol Name':
                save_data(protocol_group, {key: value})

    print("Data saved successfully.")


def load_protocol():
    def load_data(group):
        data = OrderedDict()
        keys = list(group.keys())
        keys.sort(key=lambda x: (x.startswith('Step-Group'), x))  # Ensure 'Step-Group' keys are loaded in order
        for key in keys:
            if isinstance(group[key], h5py.Group):  # Nested group
                sub_group = group[key]
                sub_data = load_data(sub_group)
                if 'Repetitions' in sub_group.attrs:
                    sub_data['Repetitions'] = sub_group.attrs['Repetitions']
                data[key] = sub_data
            else:  # Dataset
                dataset = group[key]
                if dataset.shape == ():  # Scalar dataset
                    data[key] = dataset[()]
                else:  # Regular dataset
                    data[key] = dataset[:]
        return data

    # Open the HDF5 file
    with h5py.File('protocol_data.h5', 'r') as file:
        protocol_name = 'Example_Protocol'
        protocol_group = file[protocol_name]

        # Load data
        loaded_data = load_data(protocol_group)
        loaded_data['Protocol Name'] = protocol_name

    print("Loaded Data:", loaded_data)


if __name__ == '__main__':
    save_protocol(Protocol_data)
    load_protocol()
