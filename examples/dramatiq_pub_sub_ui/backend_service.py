import time

import dramatiq
from _logger import get_logger
logger = get_logger(__name__)
from examples.dramatiq_pub_sub_ui.dramatiq_pub_sub_helpers import publish_message

TOPICS_OF_INTEREST = ["ui.event.publish_button.clicked"]

@dramatiq.actor
def print_ui_message(message, topic):
    print_statement = f"PRINT_UI_MESSAGE_SERVCICE: Received message: {message}! from topic: {topic}"
    for _ in range(100):
        print(print_statement)
    logger.info(print_statement)

    return_message = f"{message} recieved!"
    return_topic = "ui.notify.popup"

    logger.info(f"PRINT_UI_MESSAGE_SERVICE: Publishing message: {return_message} to topic: {return_topic}")
    publish_message(return_message, return_topic)
