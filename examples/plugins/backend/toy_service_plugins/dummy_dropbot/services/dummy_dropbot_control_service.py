from traits.api import HasTraits, provides

from dropbot_controller.interfaces.i_dropbot_control_mixin_service import IDropbotControlMixinService


@provides(IDropbotControlMixinService)
class DropbotDummyMixinService(HasTraits):
    """
    A mixin Class that adds methods to monitor a dropbot connection and get some dropbot information.
    """

    id = "dummy_dropbot_control"
    name = 'Dummy Dropbot Control'

    ######################################## Methods to Expose #############################################
    def print_test(self):
        print("test")