from pathlib import Path

from traits.api import provides, HasTraits
from dropbot import self_test
import datetime as dt

from microdrop_utils._logger import get_logger

from ..interfaces.i_dropbot_control_mixin_service import IDropbotControlMixinService

logger = get_logger(__name__)


def get_timestamped_path(path: [str, Path]):
    """
    Simple function to add datestamp to a given path
    """

    if not isinstance(path, Path):
        path = Path(path)

    # Generate unique filename
    timestamp = dt.datetime.utcnow().strftime('%Y-%m-%dT%H_%M_%S')

    return path.joinpath(f'results-{timestamp}')


@provides(IDropbotControlMixinService)
class DropbotSelfTestsMixinService(HasTraits):
    """
    A mixin Class that adds methods to set states for a dropbot connection and get some dropbot information.
    """

    id = "dropbot_self_tests_mixin_service"
    name = 'Dropbot Self Tests Mixin'

    ######################################## Methods to Expose #############################################
    def on_run_all_tests_request(self, report_generation_directory: str):
        """
        Method to start looking for dropbots connected using their hwids.
        """

        report_path = f"{get_timestamped_path(report_generation_directory)}.html"

        result = self_test.self_test(self.proxy)

        self_test.generate_report(result, report_path, force=True)
