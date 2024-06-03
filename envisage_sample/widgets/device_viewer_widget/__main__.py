import os

from PySide6.QtWidgets import QApplication
import sys

from . import DeviceViewerWidget

app = QApplication(sys.argv)
device_viewer_widget = DeviceViewerWidget()

# from the file dialog button
default_paths = [
    f"tests{os.sep}2x3device.svg",
    f"tests{os.sep}device_drc.svg"
]

selected_svg_path = default_paths[0]

device_viewer_widget.change_active_layer(selected_svg_path)

device_viewer_widget.show()
sys.exit(app.exec())
