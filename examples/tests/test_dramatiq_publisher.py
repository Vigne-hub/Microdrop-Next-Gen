import dramatiq
from .common import worker
import pytest


@pytest.fixture
def router_data():
    from microdrop_utils.dramatiq_pub_sub_helpers import MessageRouterData
    return MessageRouterData()


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
    with worker(dramatiq.get_broker(), worker_timeout=100):
        dramatiq.get_broker().join("default")

    # I expect the database to be populated
    assert database == {"test": "test"}

    dramatiq.get_broker().actors.clear()


