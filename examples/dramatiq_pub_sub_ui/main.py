import dramatiq
from PySide6.QtWidgets import QApplication
import sys

BROKER = dramatiq.get_broker()

# remove prometheus metrics for now
for el in dramatiq.get_broker().middleware:
    if el.__module__ == "dramatiq.middleware.prometheus":
        dramatiq.get_broker().middleware.remove(el)


from examples.dramatiq_pub_sub_ui.dramatiq_subscriber_ui import MainWindow, Orchestrator

app = QApplication(sys.argv)
window = MainWindow()
window_controller = Orchestrator(window)

worker = dramatiq.Worker(broker=BROKER, worker_timeout=1000, worker_threads=3)
worker.start()

window.show()
sys.exit(app.exec())



