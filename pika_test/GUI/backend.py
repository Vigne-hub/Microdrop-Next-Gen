import pika
import time

def process_task(ch, method, properties, body):
    print(f"{properties.correlation_id} Processing: {body}")
    # Simulating response
    time.sleep(1)  # Simulating processing time
    response = f"Processed {body} from {properties.correlation_id}"
    ch.basic_publish(exchange='', routing_key=properties.reply_to, properties=pika.BasicProperties(correlation_id=properties.correlation_id), body=response)

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Backend 1
channel.queue_declare(queue='backend1_queue')
channel.basic_consume(queue='backend1_queue', on_message_callback=process_task, auto_ack=True)

# Backend 2
channel.queue_declare(queue='backend2_queue')
channel.basic_consume(queue='backend2_queue', on_message_callback=process_task, auto_ack=True)

print('Backends are running. Waiting for tasks...')
channel.start_consuming()
