from envisage.api import ServiceOffer
from envisage.plugin import Plugin
from traits.api import List
import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from traits.trait_types import Instance

from microdrop_utils._logger import get_logger
from microdrop_utils.dramatiq_pub_sub_helpers import MessageRouterActor

# Initialize logger
logger = get_logger(__name__)

# Setup RabbitMQ broker for Dramatiq
rabbitmq_broker = RabbitmqBroker(url="amqp://guest:guest@localhost/")
dramatiq.set_broker(rabbitmq_broker)
# remove prometheus metrics for now
for el in dramatiq.get_broker().middleware:
    if el.__module__ == "dramatiq.middleware.prometheus":
        dramatiq.get_broker().middleware.remove(el)


class DropbotControllerPlugin(Plugin):
    id = 'app.dropbot_controller'
    name = 'Dropbot Plugin'

    def start(self):
        super().start() # starts plugin service
        self.dropbot_service = self._create_service() # gets services
        self.register_subscribers() # registers subscribers
        self._start_worker() # starts worker for

    def _create_service(self):
        from microdrop.services.dropbot_services import DropbotService
        return DropbotService()

    def register_subscribers(self):
        self.message_router = self.application.get_service(MessageRouterActor)
        if self.message_router is not None:
            # Use the message_router_actor instance as needed
            print("MessageRouterActor service accessed successfully.")
            for actor_name, topics_list in self.dropbot_service.actor_topics_dict.items():
                for topic in topics_list:
                    # figure out how to set up message router plugin
                    self.message_router.message_router_data.add_subscriber_to_topic(topic, actor_name)
        else:
            print("MessageRouterActor service not found.")
            return

    def disable_plugin(self):
        # TODO Method to be implemented on disabling the plugin which should stop this plugin and associated cleanup
        raise NotImplementedError

    def _start_worker(self):
        import threading
        from dramatiq import Worker

        worker = Worker(broker=rabbitmq_broker)
        worker_thread = threading.Thread(target=worker.start())
        worker_thread.daemon = True
        worker_thread.start()
