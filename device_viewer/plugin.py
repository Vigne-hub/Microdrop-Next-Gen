# Standard library imports.
import os.path

from traits.api import List
from message_router.consts import ACTOR_TOPIC_ROUTES

# Enthought library imports.
from envisage.api import Plugin, PREFERENCES, PREFERENCES_PANES, TASKS
from envisage.ui.tasks.api import TaskFactory

# local imports
from .consts import ACTOR_TOPIC_DICT

class DeviceViewerPlugin(Plugin):
    """Device Viewer plugin based on enthought envisage's The chaotic attractors plugin."""

    #### 'IPlugin' interface ##################################################

    # The plugin's unique identifier.
    id = "device_viewer"

    # The plugin's name (suitable for displaying to the user).
    name = "Device Viewer"

    #### Contributions to extension points made by this plugin ################

    preferences = List(contributes_to=PREFERENCES)
    preferences_panes = List(contributes_to=PREFERENCES_PANES)
    tasks = List(contributes_to=TASKS)
    # This plugin contributes some actors that can be called using certain routing keys.
    actor_topic_routing = List([ACTOR_TOPIC_DICT], contributes_to=ACTOR_TOPIC_ROUTES)

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
                id="device_viewer.task",
                name="Device Viewer Widget",
                factory=DeviceViewerTask,
            )
        ]
