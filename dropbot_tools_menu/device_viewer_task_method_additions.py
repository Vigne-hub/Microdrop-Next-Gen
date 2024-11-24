import json
import threading

from microdrop_utils import open_html_in_browser


def _on_self_tests_progress_triggered(self, current_message):
    """
    Method adds on to the device viewer task to listen to the self tests topic and react accordingly
    """

    message = json.loads(current_message)
    active_state = message.get('active_state')
    current_message = message.get('current_message')
    done_test_number = message.get('done_test_number')
    report_path = message.get('report_path')

    print(current_message, threading.current_thread().name)

    if active_state == False:
        self.progress_bar.current_message += f"Done running all tests. Generating report...\n"

    if current_message:
        self.progress_bar.current_message += f"Processing: {current_message}\n"

    if done_test_number is not None:
        self.progress_bar.progress = done_test_number + 1

    if report_path:
        self.progress_bar.current_message += f"Generated report at {report_path}" + "\n" + "Can close window."
        open_html_in_browser(report_path)

