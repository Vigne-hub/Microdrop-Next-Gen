"""
Tests for dropbot methods.

Notes:
    - All tests will not pass twice in a row unless you unplug power and usb connection to dropbot and plug it back
    due to halted test.
    - The other tests can be redone.
"""

import time
from dropbot import EVENT_SHORTS_DETECTED, EVENT_ENABLE, EVENT_CHANNELS_UPDATED
import numpy as np
from .common import TESTING_BOARD_ELECTRODE_CAPACTIANCE_MIN, proxy_context
import pytest


@pytest.fixture(scope='module')
def proxy():
    """
    This fixture provides a shared proxy object for all tests.
    The scope is 'module' to ensure that the same proxy is used across tests,
    and the hardware is accessed sequentially.
    """
    with proxy_context(ignore=True) as proxy:
        yield proxy


def test_dropbot_capacitance_updated(proxy):
    'Verify number of actuated channels against requested channels.'

    event = dict()

    def capacitance_updated_dump(signal):
        event["signal"] = signal["event"]

    proxy.signals.signal('capacitance-updated').connect(capacitance_updated_dump)

    proxy.update_state(capacitance_update_interval_ms=1000,
                       hv_output_selected=True,
                       hv_output_enabled=True,
                       voltage=75,
                       event_mask=EVENT_CHANNELS_UPDATED |
                                  EVENT_SHORTS_DETECTED |
                                  EVENT_ENABLE)

    time.sleep(1)

    assert event["signal"] == "capacitance-updated"


def test_actuations(proxy):
    """
    Simple actuation test. See dropbot/threshold.py for a more failsafe method in the function actuate_channels.
    """
    n_channels = 10

    channel_count = proxy.number_of_channels
    channels = np.zeros(channel_count)
    random_channels = np.random.choice(channel_count, n_channels, replace=False)
    capacitance_before_actuation = proxy.measure_capacitance()
    channels[random_channels] = 1

    ########## test triggering actuations ######################
    proxy.state_of_channels = channels
    time.sleep(0.5)
    capacitance_after_actuation = proxy.measure_capacitance()

    assert capacitance_after_actuation > capacitance_before_actuation + TESTING_BOARD_ELECTRODE_CAPACTIANCE_MIN
    capacitances = [proxy.measure_capacitance() for _ in range(10)]
    assert (sum(capacitances) / len(capacitances)) > (n_channels * TESTING_BOARD_ELECTRODE_CAPACTIANCE_MIN)

    ########## test triggering un-actuations ###################

    channels[random_channels] = 0
    proxy.state_of_channels = channels
    time.sleep(0.5)
    capacitance_after_un_actuation = proxy.measure_capacitance()

    assert capacitance_after_un_actuation < capacitance_after_actuation
    capacitances = [proxy.measure_capacitance() for _ in range(10)]
    assert (sum(capacitances) / len(capacitances)) < (n_channels * TESTING_BOARD_ELECTRODE_CAPACTIANCE_MIN)


def test_shorts_detected_signal(proxy):
    """
    Verify detect shorts signal.
    """
    event = dict()

    def shorts_detected_dump(signal):
        for key in signal.keys():
            event[key] = signal[key]

    proxy.signals.signal('shorts-detected').connect(shorts_detected_dump)

    proxy.detect_shorts()

    time.sleep(0.5)

    assert event["event"] == "shorts-detected"


def test_dropbot_halted(proxy):
    """
    Verify Halted signal.
    """
    event = dict()
    proxy.update_state(capacitance_update_interval_ms=1000,
                       hv_output_selected=True,
                       hv_output_enabled=True,
                       voltage=75,
                       event_mask=EVENT_CHANNELS_UPDATED |
                                  EVENT_SHORTS_DETECTED |
                                  EVENT_ENABLE)

    def halted_dump(signal):
        print(signal)
        for key in signal.keys():
            event[key] = signal[key]

    proxy.signals.signal('halted').connect(halted_dump)

    # Actuate all channels to saturate chip load
    proxy.state_of_channels = np.ones(proxy.number_of_channels)
    time.sleep(1)

    assert event["event"] == "halted"
    assert event['error']['name'] == "chip-load-saturated"
