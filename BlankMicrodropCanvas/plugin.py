from envisage.ids import TASKS
from envisage.plugin import Plugin
from envisage.ui.tasks.task_factory import TaskFactory
from traits.trait_types import List


class BlankMicrodropCanvasPlugin(Plugin):
    """Plugin based on enthought envisage's The chaotic attractors plugin."""

    #### 'IPlugin' interface ##################################################

    # The plugin's unique identifier.
    id = "microdrop_canvas_plugin"

    # The plugin's name (suitable for displaying to the user).
    name = "Microdrop Canvas Plugin"

    #### Contributions to extension points made by this plugin ################
    tasks = List(contributes_to=TASKS)

    def _tasks_default(self):
        from .task import MicrodropCanvasTask

        return [
            TaskFactory(
                id="microdrop_canvas.task",
                name="Microdrop Canvas",
                factory=MicrodropCanvasTask,
            )
        ]
