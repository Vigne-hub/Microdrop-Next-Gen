from traits.api import HasTraits, Range
from traitsui.api import View, Group, Item, Controller

from _logger import get_logger
logger = get_logger(__name__)


class ManualControlModel(HasTraits):
    voltage = Range(0, 1000, desc="the voltage to set on the dropbot device")
    frequency = Range(0, 100000, desc="the frequency to set on the dropbot device")


ManualControlView = View(
    Group(
        Item(
            name='voltage',
            label='Voltage (V)',
            resizable=True,
        ),

        Item(
            name='frequency',
            label='Frequency (Hz)',
            resizable=True,
        ),
    ),
    title='Manual Controls',
    resizable=True,
)


class ManualControlControl(Controller):

    def voltage_setattr(self, info, object, traitname, value):
        logger.info(f"Voltage changed to {value}")
        return super().setattr(info, object, traitname, value)

    def frequency_setattr(self, info, object, traitname, value):
        logger.info(f"Frequency changed to {value}")
        return super().setattr(info, object, traitname, value)


if __name__ == "__main__":
    model = ManualControlModel()
    view = ManualControlView
    controller = ManualControlControl()

    view.handler = controller

    model.configure_traits(view=view)
