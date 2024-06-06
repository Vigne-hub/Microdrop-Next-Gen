import os
from PySide6.QtWidgets import QApplication
import sys
from plugins.frontend.qt_widgets.device_viewer.device_viewer_qt import DeviceViewerWidget
from tests.common import TEST_PATH

if not QApplication.instance():
    app = QApplication(sys.argv)
else:
    app = QApplication.instance()

device_viewer_widget = DeviceViewerWidget()

# from the file dialog button
default_paths = [
    f"{TEST_PATH}{os.sep}device_svg_files{os.sep}2x3device.svg",
    f"{TEST_PATH}{os.sep}device_svg_files{os.sep}device_drc.svg"
]

selected_svg_path = default_paths[0]

device_viewer_widget.change_active_layer(selected_svg_path)

device_viewer_widget.show()
sys.exit(app.exec())
