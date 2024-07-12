import sys
from PySide6.QtWidgets import QApplication
from dramatiq import get_broker, Worker

from microdrop_utils.dramatiq_pub_sub_helpers import MessageRouterActor
from microdrop_utils.rmq_purger import RmqPurger


def main():
    # import the MainWindow and MainWindowController classes

    # this is the mainwindow test widget wjich will listen for messages from the dropbot connection
    # this will be packaged into a task extension to the device viewer.
    from microdrop.plugins.frontend_plugins.dropbot_status.dropbot_status_widget import DropBotControlWidget

    # this is the dropbot backend services which will hold the dropbot serial proxy connection
    from microdrop.services.dropbot_services import DropbotService

    # create an instance of the qt app
    app = QApplication(sys.argv)

    # instantiate the classes
    dropbot_control_widget = DropBotControlWidget()
    dropbot_service = DropbotService()

    # assign topics to actors
    # initialize pubsub actor
    router_actor = MessageRouterActor()

    # add subscribers to topics
    for actor_name, topics_list in dropbot_service.actor_topics_dict.items():
        for topic in topics_list:
            router_actor.message_router_data.add_subscriber_to_topic(topic, actor_name)

    # add subscribers to topics
    for actor_name, topics_list in dropbot_control_widget.actor_topics_dict.items():
        for topic in topics_list:
            router_actor.message_router_data.add_subscriber_to_topic(topic, actor_name)
    # show the window
    dropbot_control_widget.show()

    purger = RmqPurger()
    app.aboutToQuit.connect(purger.purge_all_queues)

    sys.exit(app.exec())


if __name__ == "__main__":

    BROKER = get_broker()

    for el in BROKER.middleware:
        if el.__module__ == "dramatiq.middleware.prometheus":
            BROKER.middleware.remove(el)

    worker = Worker(broker=BROKER)

    BROKER.flush_all()
    worker.start()
    main()
