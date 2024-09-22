# sys imports
import time

# enthought imports
from envisage.api import CorePlugin, Plugin, SERVICE_OFFERS, ServiceOffer
from envisage.application import Application
from traits.api import provides, HasTraits, List, observe

# plugin imports
from dropbot_controller.interfaces.i_dropbot_control_mixin_service import IDropbotControlMixinService
from dropbot_controller.plugin import DropbotControllerPlugin
from message_router.plugin import MessageRouterPlugin
from message_router.public_constants import ACTOR_TOPIC_ROUTES

# local helpers imports
from microdrop_utils.broker_server_helpers import broker_context
from microdrop_utils.dramatiq_pub_sub_helpers import publish_message


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


class DummyDropbotServicePlugin(Plugin):
    id = 'dummy_dropbot_service.plugin'
    service_offers = List(contributes_to=SERVICE_OFFERS)

    # This tells us that the plugin contributes the value of this trait to the
    # 'actor topic routes' extension point.
    actor_topic_routing = List([{"example": ["a/b", "c/d"]}], contributes_to=ACTOR_TOPIC_ROUTES)

    def _service_offers_default(self):
        """Return the service offers."""
        return [
            ServiceOffer(protocol=IDropbotControlMixinService, factory=self._create_service),
        ]

    def _create_service(self, *args, **kwargs):
        """Create an analysis service."""
        return DropbotDummyMixinService

    @observe('application:started')
    def _on_application_started(self, event):
        publish_message(message="VID:PID=16C0:", topic="dropbot/requests/start_device_monitoring")

    @observe('application:stopping')
    def _on_application_stopping(self, event):
        # create event loop
        while True:
            time.sleep(0.2)


def main(args):
    """Run the application."""

    # we will be adding a sample dummy dropbot service mixin plugin that will provide a module.submodule"

    plugins = [CorePlugin(), DropbotControllerPlugin(), DummyDropbotServicePlugin(), MessageRouterPlugin()]
    app = Application(plugins=plugins)

    with broker_context():
        app.run()


if __name__ == "__main__":
    import sys
    import os

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    main(sys.argv)
