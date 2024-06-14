import sys
from PySide6.QtWidgets import QApplication
import dramatiq

from dramatiq.brokers.rabbitmq import RabbitmqBroker

from microdrop.messaging.example_ui import MainWindow, MainWindowController

BROKER = RabbitmqBroker(url="amqp://guest:guest@localhost:5672/")
dramatiq.set_broker(BROKER)


def remove_prometheus_middleware(broker):
    for el in broker.middleware:
        if el.__module__ == "dramatiq.middleware.prometheus":
            broker.middleware.remove(el)


remove_prometheus_middleware(BROKER)

app = QApplication(sys.argv)
window = MainWindow()
window_controller = MainWindowController(window)

worker = dramatiq.Worker(broker=BROKER, worker_timeout=1000, worker_threads=10)
worker.start()

window.show()
sys.exit(app.exec())
