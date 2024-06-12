import dramatiq
from PySide6.QtWidgets import QApplication
import sys
import json

BROKER = dramatiq.get_broker()

# remove prometheus metrics for now
for el in dramatiq.get_broker().middleware:
    if el.__module__ == "dramatiq.middleware.prometheus":
        dramatiq.get_broker().middleware.remove(el)

from examples.dramatiq_pub_sub_ui.dramatiq_publisher import publish_message
from examples.dramatiq_pub_sub_ui.dramatiq_ui import MainWindow, MainWindowController
from examples.dramatiq_pub_sub_ui.backend_service import print_ui_message


@dramatiq.actor
def orchestrator_actor(message, topic):
    """
    This actor is responsible for routing messages to the correct actors. It needs access to all the relevant
    actors and their routing info. it has to be setup in the main plugin or app level.
    """

    # the routing info would be a property from the service registry associated with each service.
    # each service offer upon registry should provide this as a property
    if "ui.event.publish_button.clicked" in topic:
        publish_message(message, topic, actor_to_send="print_ui_message")

    if "ui.notify" in topic:
        publish_message(message, topic, actor_to_send="ui_listener_actor")




app = QApplication(sys.argv)
window = MainWindow()
window_controller = MainWindowController(window)

worker = dramatiq.Worker(broker=BROKER, worker_timeout=1000, worker_threads=10)
worker.start()

window.show()
sys.exit(app.exec())
