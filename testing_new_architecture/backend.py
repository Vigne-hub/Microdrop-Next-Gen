import dramatiq
import pika
from dramatiq.brokers.rabbitmq import RabbitmqBroker
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set up the RabbitMQ broker
broker = RabbitmqBroker(url="amqp://guest:guest@localhost")
# channel = broker.connection.channel()
dramatiq.set_broker(broker)


# Task processing functions
def sum_values(parameters):
    return sum(parameters.values())


def multiply_values(parameters):
    result = 1
    for value in parameters.values():
        result *= value
    return result


# Task list with method names mapped to functions
task_list = {
    "sum": sum_values,
    "multiply": multiply_values
}


# Define a Dramatiq actor
@dramatiq.actor
def process_task(task_info):
    print(f"Received task: {task_info}, processing in backend...")
    try:
        # Deserialize the task info from JSON
        task_data = json.loads(task_info)
        method = task_data.get('method')
        parameters = task_data.get('parameters')

        # Dispatch the task to the appropriate function
        if method in task_list:
            result = task_list[method](parameters)
            logging.info(f"Task processed. Method: {method}, Result: {result}")
            send_response(result)
        else:
            logging.error(f"Method '{method}' not supported.")

    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON data: {e}")
    except KeyError as e:
        logging.error(f"Missing data for {e}: {task_data}")
    except Exception as e:
        logging.error(f"An error occurred during task processing: {e}")


def send_response(result):
    broker.channel.basic_publish(
        exchange='',
        routing_key='response_backend_queue',  # Assume this queue is dedicated to receiving results
        body=str(result),
        properties=pika.BasicProperties(delivery_mode=2)  # Make messages persistent
    )
    print("Response sent back to orchestrator")
