import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker

# Setting up RabbitMQ broker
broker = RabbitmqBroker(url="amqp://guest:guest@localhost")
dramatiq.set_broker(broker)


@dramatiq.actor
def process_task(task_type, parameters):
    if task_type == "set_hv":
        voltage = parameters.get('voltage', 0)
        print(f"Setting high voltage to {voltage}V")
    elif task_type == "set_frequency":
        frequency = parameters.get('frequency', 0)
        print(f"Setting frequency to {frequency}Hz")


@dramatiq.actor
def process_advanced_task(task_type, parameters):
    # Implement the logic for more complex operations
    print(f"Executing advanced operation for {task_type} with parameters {parameters}")
