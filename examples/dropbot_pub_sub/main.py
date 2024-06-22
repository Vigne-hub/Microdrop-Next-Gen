import sys
from PySide6.QtWidgets import QApplication
from dramatiq import get_broker, Worker
from microdrop_utils.dramatiq_pub_sub_helpers import MessageRouterActor


def main():

    # import the MainWindow and MainWindowController classes from the dramatiq_ui module
    from examples.dropbot_pub_sub.ui import MainWindow, MainWindowController

    app = QApplication(sys.argv)
    # create an instance of the MainWindow class
    window = MainWindow()
    # create an instance of the MainWindowController class
    window_controller = MainWindowController(window)


    # initialize pubsub actor
    router_actor = MessageRouterActor()

    # add subscribers to topics
    for actor_name, topics_list in window_controller.actor_topics_dict.items():
        for topic in topics_list:
            router_actor.message_router_data.add_subscriber_to_topic(topic, actor_name)

    # show the window
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":

    BROKER = get_broker()

    for el in BROKER.middleware:
        if el.__module__ == "dramatiq.middleware.prometheus":
            BROKER.middleware.remove(el)

    worker = Worker(broker=BROKER)

    try:
        BROKER.flush_all()
        worker.start()
        main()

    except KeyboardInterrupt or SystemExit:
        worker.stop()
        BROKER.flush_all()
        BROKER.close()
        sys.exit(0)

    finally:
        worker.stop()
        BROKER.flush_all()
        BROKER.close()
        sys.exit(0)
