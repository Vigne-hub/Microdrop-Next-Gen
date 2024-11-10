from traits.api import HasTraits, Array, List, Dict, Bool, Int, Str, Property, TraitError, cached_property
import json
import numpy as np


class ElectrodeStateChangeRequestMessageModel(HasTraits):
    """
    Model for the JSON string sent to the electrode state change topic to request the electrode state change service.

    It should be a JSON message where the keys are the string representations of integers. and the states are
    boolean values.

    The input message will be stored in pythonized dict form. The channels will be converted to ints from string.

    >>> model = ElectrodeStateChangeRequestMessageModel(message='{"1": true, "2": false, "3": true}')
    >>> print("Valid message:", model.json_message)
    Valid message: {1: True, 2: False, 3: True}

    Example usage with invalid data (wrong key type and value type):

    >>> try:
    ...     model = ElectrodeStateChangeRequestMessageModel(message='{"1": true, "2": "false"}')
    ... except TraitError as e:
    ...     print("Validation error:", e)
    Validation error: "Message should be a dictionary with string representation of integer (numeric string) keys and Boolean values."
    """
    _json_message = Dict(Int, Bool, desc="Dict mapping integer channel ids to boolean states of each. The states "
                                         "should specify its current actuation state.")

    # We should get integer keys and Boolean values in the JSON message.
    json_message = Property(Str, observe="_json_message")

    num_available_channels = Int(desc="Number of available channels at maximum on the dropbot.")

    channels_states_boolean_mask = Property(Array, observe="_json_message", desc="boolean mask representing which channels on/off.")

    #------Property methods----------
    @cached_property
    def _get_json_message(self):
        return self._json_message

    def _set_json_message(self, json_data: Str):
        json_data_items = json.loads(json_data).items()
        if all(k.isdigit() and isinstance(v, bool) for k, v in json_data_items):
            self._json_message = {int(key): value for key, value in json_data_items}
        else:
            raise TraitError("JSON Message input should be a dictionary with string representation of "
                                         "integer (numeric string) keys and Boolean values.")

    @cached_property
    def _get_channels_states_boolean_mask(self) -> Array:
        """
        Create a Boolean mask array indicating which dropbot channels are actuated.

        Parameters:
        num_available_channels (int): The size of the output Boolean array is the total number of
                                      available channels.

        actuated_channel_numbers (list of int): The indices that should be set to True in the
                                                mask are the actuated channels.

        Returns:
            np.ndarray: A Boolean array of size `max_size` with specified `indices` set to True.
        """
        # Initialize an array of False values
        mask = np.zeros(self.num_available_channels, dtype=bool)

        # obtain the channel nums where the state is True which means it is currently ON.
        channels_on_now = [channel for channel, state in self.json_message if state]

        # Set specified indices to True
        mask[channels_on_now] = True

        return mask