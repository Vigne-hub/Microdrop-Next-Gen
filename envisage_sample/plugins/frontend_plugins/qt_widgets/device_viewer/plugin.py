
# Standard library imports.
import os.path

from traits.api import List

# Enthought library imports.
from envisage.api import Plugin
from envisage.ui.tasks.api import TaskFactory


class DeviceViewerPlugin(Plugin):
    """Device Viewer plugin based on enthought envisage's The chaotic attractors plugin."""

    # Extension point IDs.
    PREFERENCES = "envisage.preferences"
    PREFERENCES_PANES = "envisage.ui.tasks.preferences_panes"
    TASKS = "envisage.ui.tasks.tasks"

    #### 'IPlugin' interface ##################################################

    # The plugin's unique identifier.
    id = "qt_widgets.device_viewer"

    # The plugin's name (suitable for displaying to the user).
    name = "Device Viewer"

    #### Contributions to extension points made by this plugin ################

    preferences = List(contributes_to=PREFERENCES)
    preferences_panes = List(contributes_to=PREFERENCES_PANES)
    tasks = List(contributes_to=TASKS)

    ###########################################################################
    # Protected interface.
    ###########################################################################

    def _preferences_default(self):
        filename = os.path.join(os.path.dirname(__file__), "preferences.ini")
        return ["file://" + filename]

    def _preferences_panes_default(self):
        from .preferences import DeviceViewerPreferencesPane

        return [DeviceViewerPreferencesPane]

    def _tasks_default(self):
        from .task import DeviceViewerTask

        return [
            TaskFactory(
                id="qt_widgets.device_viewer.task",
                name="Device Viewer Widget",
                factory=DeviceViewerTask,
            )
        ]
