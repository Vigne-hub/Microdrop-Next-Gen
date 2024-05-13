import sys
import json
import threading

import dramatiq
import pika
import requests
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QTextEdit, QLabel, QMessageBox
from dramatiq.brokers.rabbitmq import RabbitmqBroker


class TaskSubmitter(QWidget):
    task_completed = Signal(str)

    def __init__(self):
        super().__init__()
        self.broker = RabbitmqBroker(url="amqp://guest:guest@localhost")
        dramatiq.set_broker(self.broker)
        self.initUI()
        self.thread = threading.Thread(target=self.start_consumer)
        self.thread.daemon = True
        self.thread.start()

        self.task_completed.connect(self.completed_task_popup)

    def initUI(self):
        self.setWindowTitle('Task Dispatcher')
        self.setGeometry(100, 100, 400, 200)

        # Layout
        self.layout = QVBoxLayout()

        # Input for method name
        self.method_name = QLineEdit(self)
        self.method_name.setPlaceholderText("Enter task method name")
        self.layout.addWidget(QLabel("Method Name:"))
        self.layout.addWidget(self.method_name)

        # Input for parameters as JSON
        self.parameters_input = QTextEdit(self)
        self.parameters_input.setPlaceholderText('Enter parameters in JSON format')
        self.layout.addWidget(QLabel("Parameters (JSON):"))
        self.layout.addWidget(self.parameters_input)

        # Submit button
        self.submit_button = QPushButton('Submit Task', self)
        self.submit_button.clicked.connect(self.submit_task)
        self.layout.addWidget(self.submit_button)

        self.setLayout(self.layout)

    def submit_task(self):
        method = self.method_name.text()
        try:
            parameters = json.loads(self.parameters_input.toPlainText())
        except json.JSONDecodeError:
            print("Invalid JSON")
            return

        task_info = {
            "method": method,
            "parameters": parameters
            # backend add later
        }

        self.broker.channel.basic_publish(
            exchange='',
            routing_key='frontend_task_queue',  # Assume this queue is dedicated to receiving results
            body=json.dumps(task_info),
            properties=pika.BasicProperties(delivery_mode=2)  # Make messages persistent
        )
        print("task sent to orchestrator")

    def start_consumer(self):
        connection = self.broker.connection
        channel = connection.channel()
        print("Declare queue: orc_response_queue")
        channel.queue_declare(queue='orc_response_queue')  # Ensure queue exists

        def callback_front(ch, method, properties, body):
            print("Callback front end called")
            print(body)
            self.task_completed.emit(body.decode('utf-8'))

        channel.basic_consume(queue='orc_response_queue', on_message_callback=callback_front, auto_ack=True)
        channel.start_consuming()

    def completed_task_popup(self, body):
        print("Task completed")
        QMessageBox.information(self, "Task Completed", f"Task completed with result: {body}")


if __name__ == "__main__":
    # run orchestrator and backend in different processes orc = Orchestrator() backend = Backend()
    app = QApplication(sys.argv)
    ex = TaskSubmitter()
    ex.show()
    sys.exit(app.exec())
