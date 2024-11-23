from pyface.tasks.action.api import SGroup, SMenu, TasksApplicationAction, TaskAction, TaskWindowAction
from pyface.action.api import Action
from traits.api import Property, Directory

from microdrop_utils._logger import get_logger
logger = get_logger(__name__)

from microdrop_utils.dramatiq_pub_sub_helpers import publish_message


PKG = '.'.join(__name__.split('.')[:-1])

from dropbot_controller.consts import RUN_ALL_TESTS


# Define some actions

class RunAllTests(TaskWindowAction):
    id = PKG + ".dropbot_run_all_tests"

    name = "Run all tests"

    app_data_dir = Property(Directory, observe="object.application.app_data_dir")

    def _get_app_data_dir(self):
        if self.object.application:
            return self.object.application.app_data_dir
        return None

    def perform(self, event=None):
        logger.info("Requesting running all self tests for dropbot")
        publish_message(topic=RUN_ALL_TESTS, message=self.app_data_dir)


def dropbot_tools_menu_factory():
    """
    Create a menu for the Manual Controls
    The Sgroup is a list of actions that will be displayed in the menu.
    In this case there is only one action, the help menu.
    It is contributed to the manual controls dock pane using its show help method. Hence it is a DockPaneAction.
    It fetches the specified method from teh dock pane essentially.
    """

    # create new groups with sets of actions and an id
    test_options_group = SGroup(items=[RunAllTests()], id="dropbot_tests")

    # return an SMenu object compiling each made group
    return SMenu(items=[test_options_group], id="dropbot_tools", name="Dropbot")
