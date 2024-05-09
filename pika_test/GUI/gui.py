from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QLabel
import pika
import json
import uuid


def send_message(target):
    message = json.dumps({'target': target, 'message': f'Hello from {target}'})
    corr_id = str(uuid.uuid4())
    properties = pika.BasicProperties(reply_to='gui_response_queue', correlation_id=corr_id)

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='gui_queue')
    channel.queue_declare(queue='gui_response_queue')

    channel.basic_publish(exchange='', routing_key='gui_queue', properties=properties, body=message)

    def on_response(ch, method, properties, body):
        if properties.correlation_id == corr_id:
            print(f"Response: {body}")
            label.setText(f"Response: {body.decode()}")
            connection.close()

    channel.basic_consume(queue='gui_response_queue', on_message_callback=on_response, auto_ack=True)
    channel.start_consuming()


app = QApplication([])
window = QWidget()
layout = QVBoxLayout()

button1 = QPushButton("Send to Backend 1")
button1.clicked.connect(lambda: send_message('backend1'))
layout.addWidget(button1)

button2 = QPushButton("Send to Backend 2")
button2.clicked.connect(lambda: send_message('backend2'))
layout.addWidget(button2)

label = QLabel("Responses will appear here")
layout.addWidget(label)

window.setLayout(layout)
window.show()
app.exec()
