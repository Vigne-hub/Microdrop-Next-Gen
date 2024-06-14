import dramatiq

from microdrop.messaging.publisher import publish_message


@dramatiq.actor
def orchestrator_actor(message, topic):
    if "ui.event.publish_button.clicked" in topic:
        publish_message(message, topic, actor_to_send="print_ui_message")

    if "ui.notify" in topic:
        publish_message(message, topic, actor_to_send="ui_listener_actor")
