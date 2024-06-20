import sys

import dramatiq
from PySide6.QtWidgets import QApplication


def main():
    from examples.broker import BROKER

    # import the MainWindow and MainWindowController classes from the dramatiq_ui module
    from examples.dropbot_pub_sub.ui import MainWindow, MainWindowController

    # import relevant services, this would be done via plugin registering with envsiage in a real application
    # this is done to make these actors name visible to the broker

    # initialize the pub sub message router. Again this would be done via plugin registering with envsiage
    from microdrop_utils.dramatiq_pub_sub_helpers import MessageRouterActor
    message_router_actor = MessageRouterActor()


    app = QApplication(sys.argv)
    window = MainWindow()
    window_controller = MainWindowController(window)

    message_router_actor.message_router_data.add_subscriber_to_topic('dropbot/#', 'print_dropbot_message')
    message_router_actor.message_router_data.add_subscriber_to_topic('dropbot/ports', 'make_serial_proxy')
    message_router_actor.message_router_data.add_subscriber_to_topic('dropbot/signals/connected', 'dropbot_connection_monitor')
    message_router_actor.message_router_data.add_subscriber_to_topic('dropbot/signals/disconnected', 'dropbot_connection_monitor')

    # start the dramatiq workers
    worker = dramatiq.Worker(broker=BROKER)
    worker.start()

    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    from examples.broker import BROKER

    main()
