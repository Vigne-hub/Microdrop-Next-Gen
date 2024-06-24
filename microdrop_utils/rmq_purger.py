import sys
import pika
import requests
from requests.auth import HTTPBasicAuth


class RmqPurger:
    # RabbitMQ connection details
    rabbitmq_host = 'localhost'
    username = 'guest'  # Replace with your RabbitMQ username
    password = 'guest'  # Replace with your RabbitMQ password
    management_api_url = f'http://{rabbitmq_host}:15672/api/queues'

    def purge_all_queues(self):
        # Create an HTTP session
        session = requests.Session()
        session.auth = HTTPBasicAuth(self.username, self.password)

        # Fetch the list of queues
        response = session.get(self.management_api_url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch queues: {response.status_code}, {response.text}")

        queues = response.json()

        # Connect to RabbitMQ
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.rabbitmq_host, credentials=pika.PlainCredentials(self.username, self.password)))
        channel = connection.channel()

        # Purge all queues
        for queue in queues:
            queue_name = queue['name']
            channel.queue_purge(queue=queue_name)
            print(f'Purged queue: {queue_name}')

        # Close the connection
        connection.close()

        print('All queues purged successfully.')
