# setup dramatiq broker (should be done in seperate file)
from dramatiq import get_broker

BROKER = get_broker()

import json
import subprocess
import time
import psutil
from envisage.api import Application
from .Interfaces import IAnalysisService
from .frontend_plugins.ui_plugin import UIPlugin
from .frontend_plugins.plot_view_plugin import PlotViewPlugin
from .frontend_plugins.table_view_plugin import TableViewPlugin

class MyApp(Application):
    def __init__(self, plugins, broker=None):
        super(MyApp, self).__init__(plugins=plugins)


def demo():
    # Note that fully fledged unittests for enthought services is available via https://github.com/enthought/envisage/blob/main/envisage/tests
    # This is just a simple test to show how the services can be used.

    # As well dramatiq has pytests that are comprehensive at https://github.com/Bogdanp/dramatiq/blob/master/tests
    # Again this is just a simple test just for illustration.

    ###################### Running test on dramatiq actor declaration with the broker ################################
    # Upon importing the abalysius plugin, the dramtic actor should get registerd with the dramatiq broker

    # NOTE: this fails if you improt anything that indirectly imports anything containing a dramatic actor. So loggingplugin
    # needs to be imported here as well. This is because the module with loggingplugin also has analysisplugin, so
    # analysis service (which has the dramatic actor) gets imported and thus its actor declared with the broker.

    print("#" * 100)
    print("Testing actor declaration with the broker\n")
    # before...
    assert len(BROKER.get_declared_actors()) == 0
    print(f"Declared actors before: {BROKER.get_declared_actors()}\n")

    # importing plugin with an actor
    from .backend_plugins import AnalysisPlugin, LoggingPlugin

    # after...
    assert len(BROKER.get_declared_actors()) == 1
    print(f"Declared actors after: {BROKER.get_declared_actors()}\n")

    ######### Running some tests on the application ############################################################################
    # Loading plugins
    plugins = [UIPlugin(), PlotViewPlugin(), TableViewPlugin(), AnalysisPlugin(), LoggingPlugin()]
    app = MyApp(plugins=plugins)
    app.start()
    #########TEST PLUGIN MANAGER AND SERVICE REGISTRY############################################################################
    print("#" * 100)
    print("Testing plugin manager")
    print(app.plugin_manager._plugins)
    # >> [Plugin(id='app.ui.plugin', name='UIPlugin'),
    #  Plugin(id='app.plot.view.plugin', name='Plot View Plugin'),
    #  Plugin(id='app.table.view.plugin', name='Table View Plugin'),
    #  Plugin(id='app.analysis.plugin', name='Analysis Plugin'),
    #  Plugin(id='app.logging.plugin', name='Logging Plugin')]
    print("#" * 100)
    print("Testing service registry")
    print(app.service_registry._services)
    # >> {1: ('envisage_sample.Interfaces.IAnalysisService',
    #   <envisage_sample.services.AnalysisService at 0x1f2379f2980>,
    #   {'type': 'regular'}),
    #  2: ('envisage_sample.Interfaces.IAnalysisService',
    #   <envisage_sample.services.DramatiqAnalysisService at 0x1f235c71260>,
    #   {'type': 'dramatiq', 'id': 'dramatiq_analysis_service'}),
    #  3: ('envisage_sample.Interfaces.ILoggingService',
    #   <bound method LoggingPlugin._create_service of Plugin(id='app.logging.plugin', name='Logging Plugin')>,
    #   {})}
    print("#" * 100)
    #########################################################################################################################
    # We notice the following. With the regular analysis service, we have the AnalysisService type service. Its id
    # was not declared as a property at the plugin level. So it does not get published to the yellow pages. But is
    # still available for use.
    # The DramatiqAnalysisService has an id property declared at the plugin level. So it is
    # published to the yellow pages.
    # This is a good way to control what services are available to the frontend for
    # querying.
    # Also notice that the payload_model is not avaialble for either, it was not declared in the property dict.
    ################TEST SERVICES################################################################################################
    # Another interesting thing about payload model. It gets overrided at the plugin level even if set at the service
    # class level. Eg below
    regular_task = app.get_service(IAnalysisService, query="type=='regular'")
    dramatiq_task = app.get_service(IAnalysisService, query="type=='dramatiq'")
    print("Testing properties access on services")
    print("#" * 100)
    print(f"Regular task payload overriden to be empty at plugin level: {regular_task.payload_model}")
    # >> ''
    print("#" * 100)
    print(f"Dramatic task Payload, not overriden at plugin level: {dramatiq_task.payload_model}")
    # >> '{"args_to_sum": []}'
    print("#" * 100)
    #########################################################################################################################
    # Accessing the views contributed by plugins
    ui_plugin = app.get_plugin('app.ui.plugin')
    print("Available views:", ui_plugin.views)
    print("#" * 100)
    #########################################################################################################################
    # The blocking nature of each service can be tested
    # Setting up the payload and some settings
    payload_dict = {"args_to_sum": [1, 2, 3], "sleep_time": 2}
    payload = json.dumps(payload_dict)
    N_tasks = 3
    #########################################################################################################################
    print("Testing regular task")
    result = regular_task.process_task(payload)
    # Received task: {"args_to_sum": [1, 2, 3]}, processing in backend...
    # Analysis result: 6
    print(result == 6)
    # >> True
    print("#" * 100)
    # #########################################################################################################################
    print("Testing dramatiq task regular call")
    # Dramatiq is a bit different. It can be non-blocking. So we need to wait for the result to come back on diff thread
    # and ensure the workers are running if the .send is invoked. Else same result as before
    result = dramatiq_task.process_task(payload)
    print(result == 6)
    # >> True
    print("#" * 100)
    #########################################################################################################################
    print("Testing dramatiq task send call")

    with open("results.txt", "w") as f:
        f.write("")

    # Start the dramatiq worker in a new terminal
    cmd = f'dramatiq {dramatiq_task.__class__.__module__}'

    # The os.setsid() is passed in the argument preexec_fn so
    # it's run after the fork() and before  exec() to run the shell.
    pro = subprocess.Popen(cmd)

    for i in range(N_tasks):
        dramatiq_task.process_task.send(payload)

    # process_task('{"args_to_sum": [1, 2, 3]}') result >> Message(queue_name='default', actor_name='process_task',
    # args=('{"args_to_sum": [1, 2, 3]}',), kwargs={}, options={}, message_id='ae6e0d05-a4bb-4c9c-bcc1-94b82abbe58d',
    # message_timestamp=1715811485351)
    print("#" * 100)
    # The result will be printed on the dramatiq worker process
    # You can boot up one by running the following command in a new terminal
    # dramatiq envisage_sample.services
    # Payload model should also have the response queue routing key in the future for a full implementation to
    # get back results
    #########################################################################################################################

    time.sleep(1 + (payload_dict["sleep_time"] * N_tasks))
    with open("results.txt") as f:
        results = f.readlines()
        print(results)
        for el in results:
            assert el == "Analysis result: 6\n"
        assert len(results) == N_tasks

    end_tasks(pro)
    pro.wait()


def end_tasks(process):
    # Get the process ID
    pid = process.pid

    # Use psutil to find all child processes and terminate them
    parent = psutil.Process(pid)
    for child in parent.children(recursive=True):
        child.terminate()

    # Terminate the parent process
    parent.terminate()

    # Wait for the processes to terminate (optional)
    process.wait()


if __name__ == '__main__':
    demo()
