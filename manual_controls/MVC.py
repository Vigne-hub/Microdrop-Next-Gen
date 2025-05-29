import dramatiq
from traits.api import HasTraits, Range
from traits.trait_types import Instance, Str
from traitsui.api import View, Group, Item, Controller

from microdrop_utils._logger import get_logger
from microdrop_utils.dramatiq_controller_base import generate_class_method_dramatiq_listener_actor

logger = get_logger(__name__)

from microdrop_utils.dramatiq_pub_sub_helpers import publish_message

from dropbot_controller.consts import SET_VOLTAGE, SET_FREQUENCY

from manual_controls.consts import PKG_name, PKG


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
    title=PKG_name,
    resizable=True,
)


class ManualControlControl(Controller):

    def voltage_setattr(self, info, object, traitname, value):
        publish_message(topic=SET_VOLTAGE, message=str(value))
        logger.debug(f"Requesting Voltage change to {value} V")
        return super().setattr(info, object, traitname, value)

    def frequency_setattr(self, info, object, traitname, value):
        publish_message(topic=SET_FREQUENCY, message=str(value))
        logger.debug(f"Requesting Frequency change to {value} V")
        return super().setattr(info, object, traitname, value)

    dramatiq_listener_actor = Instance(dramatiq.Actor)

    # This class is not immediately initialized here as in device viewer and in dropbot controller
    # this can be set later by whatever UI view that uses it
    listener_name = Str(f"{PKG}_listener", desc="Unique identifier for the Dramatiq actor")

    def listener_actor_routine(self, message, topic):
        print(f"Received message: {message} from topic: {topic} in Manual Control")

    def traits_init(self):
        """
        This function needs to be here to let the listener be initialized to the default value automatically.
        We just do it manually here to make the code clearer.
        We can also do other initialization routines here if needed.

        This is equivalent to doing:

        def __init__(self, **traits):
            super().__init__(**traits)

        """

        logger.info("Starting Device listener")
        self.dramatiq_listener_actor = generate_class_method_dramatiq_listener_actor(
            listener_name=self.listener_name,
            class_method=self.listener_actor_routine)


if __name__ == "__main__":
    model = ManualControlModel()
    view = ManualControlView
    controller = ManualControlControl()

    view.handler = controller

    model.configure_traits(view=view)
