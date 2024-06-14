import dramatiq


def publish_message(message, topic, actor_to_send):
    print(f"Publishing message: {message} to actor: {actor_to_send}")
    broker = dramatiq.get_broker()

    message = dramatiq.Message(
        queue_name="default",
        actor_name=actor_to_send,
        args=(message, topic),
        kwargs={},
        options={},
    )

    broker.enqueue(message)
