import dramatiq

from microdrop.messaging.publisher import publish_message


@dramatiq.actor
def print_ui_message(message, topic):
    print(f"Received message: {message}! from Topic: {topic}")

    return_message = f"{message} received!"
    return_topic = "ui.notify.popup"

    publish_message(return_message, return_topic, actor_to_send="orchestrator_actor")
