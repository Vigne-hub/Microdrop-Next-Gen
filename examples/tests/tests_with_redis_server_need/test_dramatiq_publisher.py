import dramatiq
from examples.tests.tests_with_redis_server_need.common import worker


def test_publish_message_can_send_messages_to_actors():
    # this is adapted from the dramatiq testing suite

    from microdrop_utils.dramatiq_pub_sub_helpers import publish_message

    # Given that I have a database
    database = {}

    # And an actor that can write data to that database
    @dramatiq.actor
    def put(key, value):
        database[key] = value

    # If I publish a message to the actor
    publish_message("test", "test", "put")

    # And I give the workers time to process the messages
    broker = dramatiq.get_broker()
    with worker(broker, worker_timeout=100):
        broker.join("default")

    # I expect the database to be populated
    assert database == {"test": "test"}

    broker.actors.clear()


