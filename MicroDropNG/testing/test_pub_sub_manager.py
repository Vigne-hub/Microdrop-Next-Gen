# This testing module is used to test the PubSubManager class.
# The PubSubManager class is used to manage the publishers and subscribers in the application.
# This tests publisher, subscriber creation, binding, and message publishing.
#
# Note for future: Error type everything in the code instead of just logger error messages.

from unittest.mock import MagicMock, patch
import pytest
from .common import TestMessage

'''
MONKAS
'''

@pytest.fixture(scope="module")
def setup_app():
    from ..app import MyApp
    from ..plugins.utility_plugins.pub_sub_manager_plugin import PubSubManagerPlugin

    # Assuming `MyApp` and related plugins are defined elsewhere
    plugins = [PubSubManagerPlugin()]
    app = MyApp(plugins=plugins)
    app.start()
    return app


def test_create_publisher(pubsub_manager):
    with patch('pika.BlockingConnection') as mock_connection:
        pubsub_manager.create_publisher('test_publisher', 'test_exchange')
        assert 'test_publisher' in pubsub_manager.publishers
        mock_connection.assert_called_once()


def test_publish_success(pubsub_manager):
    with patch('pika.BlockingConnection'):
        pubsub_manager.create_publisher('test_publisher', 'test_exchange')
        message = TestMessage(data="test")
        pubsub_manager.publish(message, 'test_publisher')
        _, channel, _ = pubsub_manager.publishers['test_publisher']
        channel.basic_publish.assert_called_once_with(
            exchange='test_exchange',
            routing_key='',
            body=message.model_dump_json()
        )


def test_publish_failure(pubsub_manager):
    with patch('pika.BlockingConnection'):
        message = TestMessage(data="test")
        with pytest.raises(KeyError):
            pubsub_manager.publish(message, 'nonexistent_publisher')


def test_create_subscriber(pubsub_manager):
    with patch('pika.BlockingConnection') as mock_connection:
        pubsub_manager.create_subscriber('test_subscriber')
        assert 'test_subscriber' in pubsub_manager.subscribers
        mock_connection.assert_called_once()


def test_bind_sub_to_pub_success(pubsub_manager):
    with patch('pika.BlockingConnection') as mock_connection:
        pubsub_manager.create_subscriber('test_subscriber')
        mock_channel = pubsub_manager.subscribers['test_subscriber'][1]
        mock_channel.queue_declare.return_value.method.queue = 'test_queue'

        pubsub_manager.bind_sub_to_pub('test_subscriber', 'test_exchange')

        mock_channel.queue_declare.assert_called_once_with(queue='', exclusive=True)
        mock_channel.queue_bind.assert_called_once_with(exchange='test_exchange', queue='test_queue')
        assert 'test_subscriber' in pubsub_manager.info_to_start_consumer


def test_bind_sub_to_pub_failure(pubsub_manager):
    with patch('pika.BlockingConnection'):
        with pytest.raises(KeyError):
            pubsub_manager.bind_sub_to_pub('nonexistent_subscriber', 'test_exchange')


def test_start_consumer_success(pubsub_manager):
    with patch('pika.BlockingConnection') as mock_connection:
        pubsub_manager.create_subscriber('test_subscriber')
        mock_channel = pubsub_manager.subscribers['test_subscriber'][1]
        mock_channel.queue_declare.return_value.method.queue = 'test_queue'
        pubsub_manager.bind_sub_to_pub('test_subscriber', 'test_exchange')

        mock_func = MagicMock()
        pubsub_manager.start_consumer('test_subscriber', mock_func)

        assert mock_channel.basic_consume.call_count == 1


def test_start_consumer_failure(pubsub_manager):
    with pytest.raises(ValueError):
        pubsub_manager.start_consumer('nonexistent_subscriber', MagicMock())


def test_pub_sub_service_retrieval_from_envisage_app(setup_app, pubsub_manager):
    from ..interfaces.i_pub_sub_manager_service import IPubSubManagerService

    app = setup_app
    pubsub_manager_service = app.get_service(IPubSubManagerService)

    # note: if more than one service is registered, the first one is returned. Need to add a proeprty tag on service
    # offer to query for a specific service with the same interface and use it. See envisage_sample for an example.

    assert pubsub_manager_service.__class__ == pubsub_manager.__class__

    for methods in pubsub_manager_service.__dir__():
        assert methods in pubsub_manager.__dir__()


if __name__ == '__main__':
    pytest.main()
