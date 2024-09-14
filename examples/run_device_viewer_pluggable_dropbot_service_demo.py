# Plugin imports.
import time

from dramatiq import get_broker, Worker
from envisage.api import CorePlugin, Plugin, SERVICE_OFFERS, ServiceOffer
from envisage.application import Application
from traits.api import provides, HasTraits, List, observe

from dropbot_controller.interfaces.i_dropbot_control_mixin_service import IDropbotControlMixinService
from dropbot_controller.plugin import DropbotControllerPlugin
from message_router.plugin import MessageRouterPlugin
from message_router.public_constants import ACTOR_TOPIC_ROUTES
from microdrop_utils.broker_server_helpers import init_broker_server, stop_redis_server, stop_broker_server
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

    @observe('application:stopping')
    def _initialized(self, event):
        #dc = self.application.get_plugin('dropbot_controller').dropbot_controller
        publish_message(message="VID:PID=16C0:", topic="dropbot/requests/start_device_monitoring")

        # create event loop
        while True:
            time.sleep(0.2)


class ExampleApp(Application):
    def __init__(self, plugins, broker=None):
        super().__init__(plugins=plugins)

        BROKER = get_broker()
        BROKER.flush_all()
        init_broker_server(BROKER)

        for el in BROKER.middleware:
            if el.__module__ == "dramatiq.middleware.prometheus":
                BROKER.middleware.remove(el)

        worker = Worker(broker=BROKER)
        worker.start()

    @observe('stopped')
    def cleanup(self, event):
        get_broker().flush_all()
        stop_broker_server(get_broker())


def main(args):
    """Run the application."""

    # we will be adding a sample dummy dropbot service mixin plugin that will provide a

    "module.submodule"

    plugins = [CorePlugin(), DropbotControllerPlugin(), DummyDropbotServicePlugin(), MessageRouterPlugin()]
    app = ExampleApp(plugins=plugins)
    app.run()


if __name__ == "__main__":
    import sys
    import os

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    main(sys.argv)
