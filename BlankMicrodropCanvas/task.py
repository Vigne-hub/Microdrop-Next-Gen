from pyface.tasks.api import Task
from pyface.tasks.action.api import SMenu, SMenuBar, TaskToggleGroup


class MicrodropCanvasTask(Task):
    id = "microdrop_canvas.task"

    name = "Microdrop Canvas"

    menu_bar = SMenuBar(
        SMenu(TaskToggleGroup(), id="View", name="&View")
    )

    def create_central_pane(self):
        from .widget import WhiteCanvasPane

        return WhiteCanvasPane()
