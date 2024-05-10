import pika
import time
import json
import sys

queue_name = sys.argv[1]  # Pass different queue names for different workers

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue=queue_name)

def process_task(ch, method, properties, body):
    print(f"Processing task on {queue_name}: {body}")
    #time.sleep(1)  # Simulating a task
    response = json.loads(body)
    response['result'] = f"Task completed successfully on {queue_name}"
    channel.basic_publish(exchange='', routing_key='result_queue', body=json.dumps(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue=queue_name, on_message_callback=process_task, auto_ack=False)
print(f' [*] Worker on {queue_name} is waiting for tasks. To exit press CTRL+C')
channel.start_consuming()
