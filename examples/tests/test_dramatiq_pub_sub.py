import dramatiq
from .common import worker
import pytest


@pytest.fixture
def router_data():
    from examples.dramatiq_pub_sub_ui.dramatiq_pub_sub_helpers import MessageRouterData
    return MessageRouterData()


def test_publish_message_can_send_messages_to_actors():
    # this is adapted from the dramatiq testing suite

    from examples.dramatiq_pub_sub_ui.dramatiq_pub_sub_helpers import publish_message

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


def test_add_subscriber_to_topic(router_data):
    router_data.add_subscriber_to_topic("topic1", "actor1")
    assert router_data.topic_subscriber_map["topic1"] == ["actor1"]
    router_data.add_subscriber_to_topic("topic1", "actor2")
    assert router_data.topic_subscriber_map["topic1"] == ["actor1", "actor2"]


def test_remove_subscriber_from_topic(router_data):
    router_data.add_subscriber_to_topic("topic1", "actor1")
    router_data.add_subscriber_to_topic("topic1", "actor2")
    router_data.remove_subscriber_from_topic("topic1", "actor1")
    assert router_data.topic_subscriber_map["topic1"] == ["actor2"]
    router_data.remove_subscriber_from_topic("topic1", "actor2")
    assert "topic1" not in router_data.topic_subscriber_map


def test_get_subscribers_for_topic(router_data):
    router_data.add_subscriber_to_topic("topic1", "actor1")
    router_data.add_subscriber_to_topic("topic2", "actor2")
    assert router_data.get_subscribers_for_topic("topic1") == ["actor1"]
    assert router_data.get_subscribers_for_topic("topic2") == ["actor2"]
    assert router_data.get_subscribers_for_topic("nonexistent") == []


def test_get_subscribers_for_topic_with_partial_match(router_data):
    router_data.add_subscriber_to_topic("topic1", "actor1")
    router_data.add_subscriber_to_topic("subtopic1", "actor2")
    assert router_data.get_subscribers_for_topic("topic") == ["actor1"]
    assert router_data.get_subscribers_for_topic("subtopic1") == ["actor2"]
