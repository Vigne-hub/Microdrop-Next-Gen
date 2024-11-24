from pyface.tasks.action.api import SGroup, SMenu, TaskWindowAction
from traits.api import Property, Directory, Str

from microdrop_utils._logger import get_logger

logger = get_logger(__name__)

from microdrop_utils.dramatiq_pub_sub_helpers import publish_message

PKG = '.'.join(__name__.split('.')[:-1])

from dropbot_controller.consts import RUN_ALL_TESTS, TEST_SHORTS, TEST_VOLTAGE, TEST_CHANNELS, TEST_ON_BOARD_FEEDBACK_CALIBRATION


class RunTest(TaskWindowAction):
    topic = Str(desc="topic that this test action connects to.")
    app_data_dir = Property(Directory, observe="object.application.app_data_dir")

    def _get_app_data_dir(self):
        if self.object.application:
            return self.object.application.app_data_dir
        return None

    def perform(self, event=None):
        logger.info("Requesting running all self tests for dropbot")
        publish_message(topic=self.topic, message=self.app_data_dir)


def dropbot_tools_menu_factory():
    """
    Create a menu for the Manual Controls
    The Sgroup is a list of actions that will be displayed in the menu.
    In this case there is only one action, the help menu.
    It is contributed to the manual controls dock pane using its show help method. Hence it is a DockPaneAction.
    It fetches the specified method from teh dock pane essentially.
    """

    # create new groups with all the possible dropbot self-test options as actions
    test_options_menu = SMenu(items=[
        RunTest(name="Test high voltage", topic=TEST_VOLTAGE),
        RunTest(name='On-board feedback calibration', topic=TEST_ON_BOARD_FEEDBACK_CALIBRATION),
        RunTest(name='Detect shorted channels', topic=TEST_SHORTS),
        RunTest(name="Scan test board", topic=TEST_CHANNELS),
    ],
        id="dropbot_on_board_self_tests", name="On-board self-tests",)

    # create an action to run all the test options at once
    run_all_tests = RunTest(name="Run all on-board self-tests", topic=RUN_ALL_TESTS)

    # return an SMenu object compiling each object made and put into Dropbot menu under Tools menu.
    return SMenu(items=[run_all_tests, test_options_menu], id="dropbot_tools", name="Dropbot")
