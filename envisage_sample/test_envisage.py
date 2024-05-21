import json
import subprocess
import time
import pytest
import psutil
from .app import MyApp
from .Interfaces import IAnalysisService
from .frontend_plugins.ui_plugin import UIPlugin
from .frontend_plugins.plot_view_plugin import PlotViewPlugin
from .frontend_plugins.table_view_plugin import TableViewPlugin
from .backend_plugins import AnalysisPlugin, LoggingPlugin


def start_dramatiq_worker(module_name):
    """Start the Dramatiq worker in a new session."""
    cmd = f'dramatiq {module_name}'
    pro = subprocess.Popen(cmd)
    return pro


def terminate_process_and_children(pid):
    """Terminate a process and all its children."""
    parent = psutil.Process(pid)
    for child in parent.children(recursive=True):
        child.terminate()
    parent.terminate()
    parent.wait()


def end_tasks(process):
    """Helper function to terminate the subprocess."""
    terminate_process_and_children(process.pid)


@pytest.fixture(scope="module")
def setup_app():
    # Assuming `MyApp` and related plugins are defined elsewhere
    plugins = [UIPlugin(), PlotViewPlugin(), TableViewPlugin(), AnalysisPlugin(), LoggingPlugin()]
    app = MyApp(plugins=plugins)
    app.start()
    return app


def test_plugin_manager(setup_app):
    app = setup_app
    print("Testing plugin manager")
    assert len(app.plugin_manager._plugins) == 5


def test_service_registry(setup_app):
    app = setup_app
    print("Testing service registry")
    assert len(app.service_registry._services) == 3


def test_service_properties_access_regular(setup_app):
    app = setup_app
    regular_task = app.get_service(IAnalysisService, query="type=='regular'")
    print("Testing properties access on regular service")
    assert regular_task.payload_model == ''


def test_service_properties_access_dramatiq(setup_app):
    app = setup_app
    dramatiq_task = app.get_service(IAnalysisService, query="type=='dramatiq'")
    print("Testing properties access on dramatiq service")
    assert dramatiq_task.payload_model == '{"args_to_sum": []}'


def test_view_access(setup_app):
    app = setup_app
    ui_plugin = app.get_plugin('app.ui.plugin')
    print("Available views:", ui_plugin.views)
    assert len(ui_plugin.views) > 0


def test_regular_task_processing(setup_app):
    app = setup_app
    regular_task = app.get_service(IAnalysisService, query="type=='regular'")

    payload_dict = {"args_to_sum": [1, 2, 3], "sleep_time": 2}
    payload = json.dumps(payload_dict)

    print("Testing regular task")
    result = regular_task.process_task(payload)
    assert result == 6


@pytest.fixture(scope="module")
def dramatiq_task_setup(setup_app):
    app = setup_app
    dramatiq_task = app.get_service(IAnalysisService, query="type=='dramatiq'")
    return dramatiq_task


def test_dramatiq_task_processing_regular_call(dramatiq_task_setup):
    dramatiq_task = dramatiq_task_setup

    payload_dict = {"args_to_sum": [1, 2, 3], "sleep_time": 2}
    payload = json.dumps(payload_dict)

    print("Testing dramatiq task regular call")
    result = dramatiq_task.process_task(payload)
    assert result == 6


def test_dramatiq_task_send_call(dramatiq_task_setup):
    dramatiq_task = dramatiq_task_setup

    payload_dict = {"args_to_sum": [1, 2, 3], "sleep_time": 2}
    payload = json.dumps(payload_dict)
    N_tasks = 3

    with open("results.txt", "w") as f:
        f.write("")

    # Start the Dramatiq worker
    pro = start_dramatiq_worker(dramatiq_task.__class__.__module__)

    for i in range(N_tasks):
        dramatiq_task.process_task.send(payload)

    time.sleep(1 + (payload_dict["sleep_time"] * N_tasks))
    with open("results.txt") as f:
        results = f.readlines()
        for el in results:
            assert el == "Analysis result: 6\n"
        assert len(results) == N_tasks

    end_tasks(pro)
    pro.wait()


if __name__ == "__main__":
    pytest.main()
