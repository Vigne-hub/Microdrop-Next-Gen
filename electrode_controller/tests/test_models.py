import re

import numpy as np
import pytest
from traits.api import TraitError
from ..models import ElectrodeStateChangeRequestMessageModel


def test_message_model_success():
    """Test that MessageModel accepts a valid JSON string with int keys and bool values."""
    json_data = '{"1": true, "2": false, "3": true}'
    parsed_data = {1: True, 2: False, 3: True}

    # Instantiate the model and validate
    model = ElectrodeStateChangeRequestMessageModel(json_message=json_data)
    assert model.json_message == parsed_data


def test_message_model_failure_non_boolean_value():
    """Test that MessageModel raises TraitError for JSON with non-boolean values."""
    json_data = '{"1": true, "2": "false"}'  # Value "false" is a string, not a boolean

    with pytest.raises(TraitError,
                       match=re.escape("JSON Message input should be a dictionary with string representation of "
                                       "integer (numeric string) keys and Boolean values.")):
        ElectrodeStateChangeRequestMessageModel(json_message=json_data)


def test_get_boolean_channels_states_mask():
    """Test that MessageModel returns the correct mask for the channels and states based on the input json string and
    max available channels specified
    """
    json_data = '{"0": true, "1": false, "9": true}'
    max_channels = 10

    # Instantiate the model and validate
    model = ElectrodeStateChangeRequestMessageModel(json_message=json_data, num_available_channels=max_channels)
    assert np.all(
        model.channels_states_boolean_mask ==
        np.array([True, False, False, False, False, False, False, False, False, True])
    )


def test_get_boolean_channels_states_mask_zero_on():
    """Test that MessageModel returns the correct mask for the channels and states based on the input json string and
    max available channels specified
    """
    json_data = '{"0": false, "1": false, "9": false}'
    max_channels = 10

    # Instantiate the model and validate
    model = ElectrodeStateChangeRequestMessageModel(json_message=json_data, num_available_channels=max_channels)
    assert np.all(
        model.channels_states_boolean_mask ==
        np.array([False, False, False, False, False, False, False, False, False, False])
    )
