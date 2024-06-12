import dramatiq


def publish_message(routing_info, message, actor_to_send="orchestrator_actor"):
    print(f"Publishing message: {message} to route: {routing_info}")
    broker = dramatiq.get_broker()

    message = dramatiq.Message(
        queue_name="default",
        actor_name=actor_to_send,
        args=(routing_info, message),
        kwargs={},
        options={},
    )

    broker.enqueue(message)


if __name__ == "__main__":
    publish_message("ui.notify", "Hello world!")
