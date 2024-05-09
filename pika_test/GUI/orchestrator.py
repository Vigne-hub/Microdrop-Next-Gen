import pika
import json

def orchestrator_callback(ch, method, properties, body):
    message = json.loads(body)
    print(f"Orchestrator received: {message}")
    # Routing logic
    if message['target'] == 'backend1':
        ch.basic_publish(exchange='', routing_key='backend1_queue', body=body, properties=properties)
    elif message['target'] == 'backend2':
        ch.basic_publish(exchange='', routing_key='backend2_queue', body=body, properties=properties)

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='gui_queue')
channel.queue_declare(queue='backend1_queue')
channel.queue_declare(queue='backend2_queue')

channel.basic_consume(queue='gui_queue', on_message_callback=orchestrator_callback, auto_ack=True)

print('Orchestrator is running. Waiting for messages...')
channel.start_consuming()
