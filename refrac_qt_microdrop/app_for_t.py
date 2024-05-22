from envisage.api import Application
from refrac_qt_microdrop.backend_plugins.dropbot_controller_plugin import DropbotPlugin
from refrac_qt_microdrop.frontend_plugins.example_dropbot_frontend import FrontendPlugin
from PySide6.QtWidgets import QApplication, QMainWindow


class MyApp(Application):
    def __init__(self, plugins):
        super(MyApp, self).__init__(plugins=plugins)


def main():
    app = QApplication([])
    plugins = [DropbotPlugin(), FrontendPlugin()]
    my_app = MyApp(plugins=plugins)
    my_app.start()

    # Debugging: Print registered services
    print("Registered services after start:")
    for service_id, service_data in my_app.service_registry._services.items():
        print(f"Service ID: {service_id}, Protocol: {service_data[0]}, Service: {service_data[1]}")

    main_window = my_app.get_service(QMainWindow)
    if main_window is not None:
        print("QMainWindow service found:", main_window)
        main_window.show()
        app.exec()
    else:
        print("QMainWindow service not found")

    my_app.stop()


if __name__ == '__main__':
    main()
