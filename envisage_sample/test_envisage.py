import pytest


@pytest.fixture(scope="module")
def results_file():
    from pathlib import Path
    test_results = Path(__file__).parent / "results.txt"
    with open(test_results, "w") as f:
        f.write("")

    return test_results


@pytest.fixture(scope="module")
def setup_app():
    from .frontend_plugins.ui_plugin import UIPlugin
    from .frontend_plugins.plot_view_plugin import PlotViewPlugin
    from .frontend_plugins.table_view_plugin import TableViewPlugin
    from .backend_plugins.logging_plugin import LoggingPlugin
    from .backend_plugins.analysis_plugin import AnalysisPlugin
    from .app import MyApp

    # Assuming `MyApp` and related plugins are defined elsewhere
    plugins = [UIPlugin(), PlotViewPlugin(), TableViewPlugin(), AnalysisPlugin(), LoggingPlugin()]
    app = MyApp(plugins=plugins)
    app.start()
    return app


def test_analysis_plugin_import():
    from .common import BROKER

    print("#" * 100)
    print("Testing actor declaration with the broker\n")

    # before...
    assert len(BROKER.get_declared_actors()) == 0
    print(f"Declared actors before: {BROKER.get_declared_actors()}\n")

    # importing plugin with an actor
    from .backend_plugins.analysis_plugin import AnalysisPlugin

    # after...
    assert len(BROKER.get_declared_actors()) == 1
    print(f"Declared actors after: {BROKER.get_declared_actors()}\n")


def test_plugin_manager(setup_app):
    app = setup_app
    print("Testing plugin manager")
    assert len(app.plugin_manager._plugins) == 5


def test_service_registry(setup_app):
    app = setup_app
    print("Testing service registry")
    assert len(app.service_registry._services) == 3


def test_service_properties_access_regular(setup_app):

    from .backend_plugins.analysis_plugin import IAnalysisService

    app = setup_app
    regular_task = app.get_service(IAnalysisService, query="type=='regular'")
    print("Testing properties access on regular service")
    assert len(regular_task.payload_model) == 0


def test_service_properties_access_dramatiq(setup_app):

    from .backend_plugins.analysis_plugin import IAnalysisService

    app = setup_app
    dramatiq_task = app.get_service(IAnalysisService, query="type=='dramatiq'")
    print("Testing properties access on dramatiq service")
    assert len(dramatiq_task.payload_model) != 0


def test_view_access(setup_app):
    app = setup_app
    ui_plugin = app.get_plugin('app.ui.plugin')
    print("Available views:", ui_plugin.views)
    assert len(ui_plugin.views) > 0


def test_regular_task_processing(setup_app):

    from .backend_plugins.analysis_plugin import IAnalysisService

    app = setup_app
    regular_task = app.get_service(IAnalysisService, query="type=='regular'")

    payload = {"args_to_sum": [1, 2, 3], "sleep_time": 2}

    print("Testing regular task")
    result = regular_task.process_task(payload)
    assert result == 6


@pytest.fixture(scope="module")
def dramatiq_task_setup(setup_app):

    from .interfaces.i_analysis_service import IAnalysisService

    app = setup_app
    dramatiq_task = app.get_service(IAnalysisService, query="type=='dramatiq'")
    return dramatiq_task


def test_dramatiq_task_processing_regular_call(dramatiq_task_setup):
    dramatiq_task = dramatiq_task_setup

    payload = {"args_to_sum": [1, 2, 3], "sleep_time": 2}

    print("Testing dramatiq task regular call")
    result = dramatiq_task.process_task(payload)
    assert result == 6


def test_dramatiq_task_send_call(dramatiq_task_setup, results_file):

    from .common import worker, BROKER
    import time

    dramatiq_task = dramatiq_task_setup

    payload = {"args_to_sum": [1, 2, 3], "sleep_time": 2, "reply": 0, "results_file": str(results_file)}
    N_tasks = 3

    with worker(broker=BROKER, queues=None, worker_timeout=1000, worker_threads=N_tasks) as test_worker:

        for i in range(N_tasks):
            dramatiq_task.process_task.send(payload)
        test_worker.join()

    time.sleep(1)

    with open(results_file) as f:
        results = f.readlines()
        for el in results:
            assert el == "Analysis result: 6\n"
        assert len(results) == N_tasks


if __name__ == "__main__":
    pytest.main()
