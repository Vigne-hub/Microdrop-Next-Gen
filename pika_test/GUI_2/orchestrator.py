import pika
import threading
import json
import uuid

class Orchestrator:
    def __init__(self):
        self.gui_connections = {}
        self.backend_connections = {}
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='result_queue')
        self.start_consumer()

    def register_gui(self, gui):
        gui_id = str(uuid.uuid4())
        self.gui_connections[gui_id] = gui
        return gui_id

    def register_backend(self, backend_queue):
        backend_id = str(uuid.uuid4())
        self.backend_connections[backend_id] = backend_queue
        return backend_id

    def send_task(self, task, backend_queue):
        self.channel.basic_publish(exchange='', routing_key=self.backend_connections[backend_queue], body=json.dumps(task))

    def start_consumer(self):
        thread = threading.Thread(target=self.consume)
        thread.daemon = True
        thread.start()

    def consume(self):
        self.channel.basic_consume(queue='result_queue', on_message_callback=self.on_response, auto_ack=True)
        self.channel.start_consuming()

    def on_response(self, ch, method, properties, body):
        response = json.loads(body)
        gui_id = response['gui_id']
        if gui_id in self.gui_connections:
            self.gui_connections[gui_id].display_result(response['result'])
