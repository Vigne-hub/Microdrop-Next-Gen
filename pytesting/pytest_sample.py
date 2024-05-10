import pytest
from unittest import mock
import asyncio


# Mock classes for SignalingHub and Plugin for demonstration purposes
class SignalingHub:
    def __init__(self):
        self.listeners = {}

    def register_listener(self, signal_name, callback, priority=0):
        if signal_name not in self.listeners:
            self.listeners[signal_name] = []
        self.listeners[signal_name].append((callback, priority))
        self.listeners[signal_name].sort(key=lambda x: x[1])

    async def emit(self, signal_name, data):
        if signal_name in self.listeners:
            for listener, _ in self.listeners[signal_name]:
                if asyncio.iscoroutinefunction(listener):
                    await listener(data)
                else:
                    listener(data)


# Test suite
def test_signal_emission_and_reception():
    hub = SignalingHub()
    received = False

    def listener(data):
        nonlocal received
        received = True
        assert data == "test_data", "Data received is not as expected"

    hub.register_listener("test_signal", listener)
    hub.emit("test_signal", "test_data")
    assert received, "Signal was not received by the listener"


def test_priority_handling():
    hub = SignalingHub()
    order = []

    def high_priority_listener(data):
        order.append('high')

    def low_priority_listener(data):
        order.append('low')

    hub.register_listener("test_signal", low_priority_listener, priority=10)
    hub.register_listener("test_signal", high_priority_listener, priority=1)
    hub.emit("test_signal", None)
    assert order == ['high', 'low'], "Priority handling failed: Order of execution is incorrect"


def test_signal_overload():
    hub = SignalingHub()
    count = 0

    def listener(data):
        nonlocal count
        count += 1

    hub.register_listener("test_signal", listener)
    for _ in range(1000):
        hub.emit("test_signal", None)
    assert count == 1000, "Not all signals were handled correctly"


@pytest.mark.asyncio
async def test_async_signal_handling():
    hub = SignalingHub()

    async def async_listener(data):
        await asyncio.sleep(1)  # Simulate async operation
        assert data == "async_test", "Async data handling failed"

    hub.register_listener("async_test_signal", async_listener)
    await hub.emit("async_test_signal", "async_test")


def test_plugin_integration():
    hub = SignalingHub()
    mock_plugin = mock.Mock()

    # Ensure the plugin registers a listener to the signaling hub
    def plugin_listener(data):
        assert data == "plugin_data", "Plugin did not receive correct data"

    # Adjust the mock setup to reflect registration interaction
    mock_plugin.register_listener = mock.MagicMock(
        side_effect=lambda signal, listener: hub.register_listener(signal, listener))

    # Simulate plugin registration to the hub
    mock_plugin.register_listener("plugin_signal", plugin_listener)

    # Emit a signal to trigger the listener
    hub.emit("plugin_signal", "plugin_data")

    # Verify the mock's register_listener method was called as expected
    mock_plugin.register_listener.assert_called_once_with("plugin_signal", plugin_listener)

