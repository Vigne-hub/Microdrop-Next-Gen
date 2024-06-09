import pytest
from PySide6.QtWidgets import QApplication
from unittest.mock import MagicMock

"""
This testing module is used to test the Plugin structure with an initial focus on the dropbot plugin.
The DropbotControllerPlugin is a plugin that provides the DropbotControllerService to the application.
This tests the plugin registration, service registration, and service methods
"""


@pytest.fixture(scope="module")
def app():
    """Fixture for creating the Qt application."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def envisage_app():
    """Fixture for creating the Envisage application with plugins."""
    from ..app import MyApp
    from ..plugins.utility_plugins.pub_sub_manager_plugin import PubSubManagerPlugin
    from ..plugins.backend_plugins.dropbot_controller import DropbotControllerPlugin

    # Initialize the application with the required plugins
    plugins = [PubSubManagerPlugin(), DropbotControllerPlugin()]
    app = MyApp(plugins=plugins)
    app.start()
    return app


def test_plugins_registered(envisage_app):
    """Test if plugins are registered correctly in the Envisage application."""
    assert envisage_app.plugin_manager.get_plugin('app.dropbot_controller') is not None


def test_dropbot_service_registered(envisage_app):
    """Test if DropbotControllerService is registered in the application."""
    from microdrop.interfaces.i_dropbot_controller_service import IDropbotControllerService
    dropbot_service = envisage_app.get_service(IDropbotControllerService)
    assert dropbot_service is not None


def test_dropbot_service_methods(envisage_app):
    """Test if DropbotControllerService methods are callable and work as expected."""
    from microdrop.interfaces.i_dropbot_controller_service import IDropbotControllerService
    dropbot_service = envisage_app.get_service(IDropbotControllerService)
    assert dropbot_service is not None

    # Mock the dropbot_actor to avoid actual message sending during tests
    dropbot_service.dropbot_actor.process_task = MagicMock()

    # Test poll_voltage
    dropbot_service.poll_voltage()
    dropbot_service.dropbot_actor.process_task.send.assert_called_with(
        {"name": "poll_voltage", "args": [], "kwargs": {}})

    # Test set_voltage
    dropbot_service.set_voltage(5)
    dropbot_service.dropbot_actor.process_task.send.assert_called_with(
        {"name": "set_voltage", "args": [5], "kwargs": {}})

    # Test set_frequency
    dropbot_service.set_frequency(1000)
    dropbot_service.dropbot_actor.process_task.send.assert_called_with(
        {"name": "set_frequency", "args": [1000], "kwargs": {}})

    # Test set_hv
    dropbot_service.set_hv(True)
    dropbot_service.dropbot_actor.process_task.send.assert_called_with({"name": "set_hv", "args": [True], "kwargs": {}})

    # Test get_channels
    dropbot_service.get_channels()
    dropbot_service.dropbot_actor.process_task.send.assert_called_with(
        {"name": "get_channels", "args": [], "kwargs": {}})

    # Test set_channels
    channels = [1, 2, 3]
    dropbot_service.set_channels(channels)
    dropbot_service.dropbot_actor.process_task.send.assert_called_with(
        {"name": "set_channels", "args": [channels], "kwargs": {}})

    # Test set_channel_single
    dropbot_service.set_channel_single(1, True)
    dropbot_service.dropbot_actor.process_task.send.assert_called_with(
        {"name": "set_channel_single", "args": [1, True], "kwargs": {}})

    # Test droplet_search
    dropbot_service.droplet_search(0.5)
    dropbot_service.dropbot_actor.process_task.send.assert_called_with(
        {"name": "droplet_search", "args": [0.5], "kwargs": {}})


if __name__ == '__main__':
    pytest.main()
