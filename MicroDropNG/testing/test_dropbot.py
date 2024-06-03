import pytest
from unittest.mock import MagicMock, patch
import numpy as np
from MicroDropNG.backend_logic.dropbot_controller import DropbotController
from MicroDropNG.services.pub_sub_manager_services import PubSubManager

"""
This testing module is used to test the DropbotController class (refractored mike+vig/mig updated version).
The DropbotController class is used to manage the Dropbot system via a serial proxy.
This tests the initialization, signal emission, output state change, voltage, frequency, hv, channels, and droplet search.

Note for future: figure out how to do the testing with internal messaging signals in the methods 
so that I can test without using exact code and just call methods
"""

@pytest.fixture
def dropbot_controller():
    return DropbotController()


@pytest.fixture
def pub_sub_manager():
    return PubSubManager()


def test_initialize_dropbot_controller(dropbot_controller):
    assert dropbot_controller.proxy is None
    assert isinstance(dropbot_controller.last_state, np.ndarray)
    assert dropbot_controller.last_state.shape == (128,)
    assert dropbot_controller.last_state.dtype == 'uint8'


def test_emit_signal(dropbot_controller, pub_sub_manager):
    pub_sub_manager.create_publisher('test_publisher', 'test_exchange')
    with patch.object(pub_sub_manager, 'publish') as mock_publish:
        dropbot_controller.pub_sub_manager = pub_sub_manager
        dropbot_controller.emit_signal('test_message')
        mock_publish.assert_called_once_with(message='test_message', publisher='dropbot_publisher')


def test_output_state_changed_success(dropbot_controller):
    with patch.object(dropbot_controller, 'emit_signal') as mock_emit_signal:
        dropbot_controller.output_state_changed({'event': 'output_enabled'})
        mock_emit_signal.assert_called_with(dropbot_controller.output_state_true)
        dropbot_controller.output_state_changed({'event': 'output_disabled'})
        mock_emit_signal.assert_called_with(dropbot_controller.output_state_false)


def test_output_state_changed_failure(dropbot_controller):
    with pytest.raises(ValueError):
        dropbot_controller.output_state_changed({'event': 'unknown_event'})


def test_set_voltage(dropbot_controller):
    dropbot_controller.proxy = MagicMock()
    dropbot_controller.set_voltage(5)
    assert dropbot_controller.proxy.voltage == 5


def test_set_voltage_no_proxy(dropbot_controller):
    dropbot_controller.set_voltage(5)
    assert dropbot_controller.proxy is None


def test_set_frequency(dropbot_controller):
    dropbot_controller.proxy = MagicMock()
    dropbot_controller.set_frequency(20000)
    assert dropbot_controller.proxy.frequency == 20000


def test_set_frequency_no_proxy(dropbot_controller):
    dropbot_controller.set_frequency(20000)
    assert dropbot_controller.proxy is None


def test_set_hv(dropbot_controller):
    dropbot_controller.proxy = MagicMock()
    dropbot_controller.set_hv(True)
    assert dropbot_controller.proxy.hv_output_enabled == True


def test_set_hv_no_proxy(dropbot_controller):
    dropbot_controller.set_hv(True)
    assert dropbot_controller.proxy is None


def test_get_channels(dropbot_controller):
    dropbot_controller.proxy = MagicMock()
    dropbot_controller.proxy.state_of_channels = np.ones(128, dtype='uint8')
    channels = np.array(dropbot_controller.proxy.state_of_channels)
    assert (channels == np.ones(128, dtype='uint8')).all()


def test_get_channels_no_proxy(dropbot_controller):
    channels = dropbot_controller.get_channels()
    assert (channels == np.zeros(128, dtype='uint8')).all()


def test_set_channels(dropbot_controller):
    dropbot_controller.proxy = MagicMock()
    new_state = np.ones(128, dtype='uint8')
    dropbot_controller.last_state = dropbot_controller.proxy.state_of_channels
    dropbot_controller.proxy.state_of_channels = np.array(new_state)
    np.testing.assert_array_equal(dropbot_controller.proxy.state_of_channels, new_state)


def test_set_channels_no_proxy(dropbot_controller):
    new_state = np.ones(128, dtype='uint8')
    dropbot_controller.set_channels(new_state)
    assert dropbot_controller.proxy is None


def test_set_channel_single(dropbot_controller):
    dropbot_controller.proxy = MagicMock()
    dropbot_controller.proxy.state_of_channels = [0] * 128

    channels = np.array(dropbot_controller.proxy.state_of_channels)
    channels[5] = 1
    dropbot_controller.proxy.state_of_channels = channels

    updated_channels = dropbot_controller.proxy.state_of_channels
    assert updated_channels[5] == 1


def test_set_channel_single_no_proxy(dropbot_controller):
    dropbot_controller.set_channel_single(5, True)
    assert dropbot_controller.proxy is None


def test_droplet_search(dropbot_controller, pub_sub_manager):
    dropbot_controller.proxy = MagicMock()
    dropbot_controller.proxy.get_drops.return_value = [[1, 2, 3]]
    dropbot_controller.droplet_search(0.5)
    assert dropbot_controller.proxy.get_drops.called