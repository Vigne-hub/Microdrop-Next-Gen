from pathlib import Path

from envisage.ui.tasks.tasks_application import TasksApplication, DEFAULT_STATE_FILENAME
from pyface.action.schema.schema import SMenuBar, SMenu
from pyface.tasks.action.task_toggle_group import TaskToggleGroup


class MicrodropCanvasTaskApplication(TasksApplication):
    """Device Viewer application based on enthought envisage's The chaotic attractors Tasks application."""

    #### 'IApplication' interface #############################################

    # The application's globally unique identifier.
    id = "microdrop_canvas.app"

    # The application's user-visible name.
    name = "Microdrop Canvas"

    always_use_default_layout = False

    #: The directory on the local file system used to persist window layout
    #: information.
    state_location = Path.home() / ".microdrop_next_gen_blank_canvas"

    #: The filename that the application uses to persist window layout
    #: information.
    state_filename = DEFAULT_STATE_FILENAME

    menu_bar = SMenuBar(
        SMenu(TaskToggleGroup(), id="View", name="&View")
    )
