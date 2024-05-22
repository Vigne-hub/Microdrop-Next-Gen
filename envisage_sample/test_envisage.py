import json
import time

import dramatiq
import pytest
from .app import MyApp
from .Interfaces import IAnalysisService
from .frontend_plugins.ui_plugin import UIPlugin
from .frontend_plugins.plot_view_plugin import PlotViewPlugin
from .frontend_plugins.table_view_plugin import TableViewPlugin
from .backend_plugins import AnalysisPlugin, LoggingPlugin
from .common import worker, BROKER

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

    payload = {"args_to_sum": [1, 2, 3], "sleep_time": 2}

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

    payload = {"args_to_sum": [1, 2, 3], "sleep_time": 2}

    print("Testing dramatiq task regular call")
    result = dramatiq_task.process_task(payload)
    assert result == 6


def test_dramatiq_task_send_call(dramatiq_task_setup):
    dramatiq_task = dramatiq_task_setup

    payload = {"args_to_sum": [1, 2, 3], "sleep_time": 2, "reply": 0}
    N_tasks = 3

    with open("results.txt", "w") as f:
        f.write("")

    with worker(broker=BROKER, queues=None, worker_timeout=1000, worker_threads=N_tasks) as test_worker:

        for i in range(N_tasks):
            dramatiq_task.process_task.send(payload)
        test_worker.join()

    time.sleep(0.2)

    with open("results.txt") as f:
        results = f.readlines()
        for el in results:
            assert el == "Analysis result: 6\n"
        assert len(results) == N_tasks


if __name__ == "__main__":
    pytest.main()
