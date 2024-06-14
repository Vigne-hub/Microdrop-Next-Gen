import json

import dramatiq

from examples.dramatiq_pub_sub_ui.dramatiq_publisher import publish_message


@dramatiq.actor
def print_ui_message(message, topic):
    print(f"Received message: {message}! from Topic: {topic}")

    return_message = f"{message} recieved!"
    return_topic = "ui.notify.popup"

    publish_message(return_message, return_topic, actor_to_send="orchestrator_actor")
