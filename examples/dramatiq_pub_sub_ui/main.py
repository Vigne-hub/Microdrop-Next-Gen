import dramatiq
from PySide6.QtWidgets import QApplication
import sys

BROKER = dramatiq.get_broker()

# remove prometheus metrics for now
for el in dramatiq.get_broker().middleware:
    if el.__module__ == "dramatiq.middleware.prometheus":
        dramatiq.get_broker().middleware.remove(el)


# import the MainWindow and MainWindowController classes from the dramatiq_ui module
from examples.dramatiq_pub_sub_ui.dramatiq_ui import MainWindow, MainWindowController

# import relevant services, this would be done via plugin registering with envsiage in a real application
# this is done to make these actors name visible to the broker

from examples.dramatiq_pub_sub_ui.backend_service import print_ui_message, TOPICS_OF_INTEREST

# initialize the pub sub message router. Again this would be done via plugin registering with envsiage
from examples.dramatiq_pub_sub_ui.dramatiq_pub_sub_helpers import MessageRouterActor
message_router_actor = MessageRouterActor()


app = QApplication(sys.argv)
window = MainWindow()
window_controller = MainWindowController(window)

# register the subscribers in window controller to the appropriate topics. On plugin startup
for topic in window_controller.topics_of_interest:
    message_router_actor.message_router_data.add_subscriber_to_topic(topic, window_controller.ui_listener_actor.actor_name)

# on plugin startup, register the print_ui_message actor to the appropriate topics
for topic in TOPICS_OF_INTEREST:
    message_router_actor.message_router_data.add_subscriber_to_topic(topic, print_ui_message.actor_name)



# start the dramatiq workers
worker = dramatiq.Worker(broker=BROKER, worker_timeout=100000, worker_threads=10)
worker.start()

window.show()
sys.exit(app.exec())
