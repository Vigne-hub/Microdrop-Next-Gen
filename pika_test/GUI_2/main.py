import sys
import subprocess
from PySide6.QtWidgets import QApplication
from gui import GUI
from orchestrator import Orchestrator


def start_backend(queue_name):
    """
    Start a backend worker process with a specific queue name.
    """
    return subprocess.Popen(['python', 'backend.py', queue_name])


def main():
    # Start RabbitMQ service manually or ensure it's running before this script

    # Start two backend workers with unique queue names
    backend1 = start_backend('backend_queue_1')
    backend2 = start_backend('backend_queue_2')

    # Start the application
    app = QApplication(sys.argv)
    orchestrator = Orchestrator()

    # Register backends with unique queue names
    backend1 = orchestrator.register_backend('backend_queue_1')
    backend2 = orchestrator.register_backend('backend_queue_2')

    # Create two GUIs with references to both backends
    gui1 = GUI(orchestrator, [backend1, backend2], "GUI 1")
    gui2 = GUI(orchestrator, [backend1, backend2], "GUI 2")

    # Execute the Qt application loop
    result = app.exec()

    return result


if __name__ == "__main__":
    sys.exit(main())
