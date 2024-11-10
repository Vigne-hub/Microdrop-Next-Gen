import re

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

    with pytest.raises(TraitError, match=re.escape("JSON Message input should be a dictionary with string representation of "
                                         "integer (numeric string) keys and Boolean values.")):

        ElectrodeStateChangeRequestMessageModel(json_message=json_data)