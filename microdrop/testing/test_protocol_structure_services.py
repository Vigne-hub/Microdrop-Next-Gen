import unittest
from json import JSONDecodeError

import pytest
from unittest.mock import MagicMock, patch
import json
import os

from pydantic import BaseModel
from traits.trait_errors import TraitError

from microdrop.pydantic_models.base_signal_model import SignalNameModel
from microdrop.services.protocol_grid_structure_services import ProtocolGridStructureService
from microdrop.services.pub_sub_manager_services import PubSubManager


@pytest.fixture
def pub_sub_manager():
    return PubSubManager()


@pytest.fixture
def protocol_service(pub_sub_manager):
    return ProtocolGridStructureService(pub_sub_manager)


def test_add_step(protocol_service):
    protocol_service.add_step('1', ['1', '2'])
    assert protocol_service.steps == ['1']
    assert protocol_service.electrodes_on['1'] == ['1', '2']


def test_add_step_type_error(protocol_service):
    with pytest.raises(TraitError):
        protocol_service.add_step(1, ['1', '2'])  # step should be an int


def test_save_protocol(protocol_service):
    with patch("builtins.open", unittest.mock.mock_open()) as mocked_file:
        protocol_service.save_protocol("protocol_1") # file_name is not used in the method
        mocked_file.assert_called_with(os.path.join(protocol_service.file_save_dir, protocol_service.file_name), "w")


def test_save_protocol_failure(protocol_service):
    with patch("builtins.open", unittest.mock.mock_open()) as mocked_file:
        mocked_file.side_effect = IOError("File write error")
        with pytest.raises(IOError):
            protocol_service.save_protocol("test_protocol")


def test_load_protocol(protocol_service, pub_sub_manager):
    def load_request_received(message):
        assert message == 'received'
    pub_sub_manager.create_publisher("update_protocol_view_signal", "to_protocol_view")
    pub_sub_manager.create_subscriber("sub")
    pub_sub_manager.bind_sub_to_pub("sub", "to_protocol_view")
    pub_sub_manager.start_consumer("sub", load_request_received("received"))
    table_json = SignalNameModel(Signal="signal_name", Arg1="test1", Arg2="test2", Arg3="test3")
    pub_sub_manager.publish(table_json, "update_protocol_view_signal")


def test_load_protocol_failure(protocol_service, pub_sub_manager):
    with patch("builtins.open", unittest.mock.mock_open()) as mocked_file:
        mocked_file.side_effect = IOError("File read error")
        with pytest.raises(IOError):
            protocol_service.load_protocol("test_path")


def test_save_to_file(protocol_service):
    protocol_service.file_name = "test_protocol"
    with patch("builtins.open", unittest.mock.mock_open()) as mocked_file:
        protocol_service.save_to_file('{"key": "value"}', "test_protocol")
        mocked_file.assert_called_with(os.path.join(protocol_service.file_save_dir, "test_protocol"), "w")


def test_save_to_file_failure(protocol_service):
    protocol_service.file_name = "test_protocol"
    with patch("builtins.open", unittest.mock.mock_open()) as mocked_file:
        mocked_file.side_effect = IOError("File write error")
        with pytest.raises(IOError):
            protocol_service.save_to_file('{"key": "value"}', "test_protocol")


def test_on_cell_changed(protocol_service):
    args = ['{"1": {"Description": "desc1", "Duration": 30, "Voltage": 100, "Frequency": 10000}}']
    protocol_service.on_cell_changed(args)
    expected_data = {"1": {"Description": "desc1", "Duration": 30, "Voltage": 100, "Frequency": 10000}}
    assert protocol_service.protocol_data == expected_data


def test_on_cell_changed_JDecode_error(protocol_service):
    with pytest.raises(JSONDecodeError):
        protocol_service.on_cell_changed("this should be a list")


def test_on_electrode_clicked(protocol_service):
    args = []
    kwargs = {"steps": ['1'], "electrodes": ["1", "2"]}
    protocol_service.on_electrode_clicked(args, kwargs)
    assert protocol_service.electrodes_on['1'] == ["1", "2"]


def test_publish_electrodes_active_to_device_view_key_error(protocol_service):
    kwargs = {"active rows": "should be a list"}
    with pytest.raises(KeyError):
        protocol_service.publish_electrodes_active_to_device_view(kwargs)
