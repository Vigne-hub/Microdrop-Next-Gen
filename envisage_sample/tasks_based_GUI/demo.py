from pyface.tasks.api import Task
from pyface.api import PythonEditor
from pyface.tasks.api import TaskPane
from traits.api import Instance


class ExampleTask(Task):
    id = 'example.example_task'

    name = 'Python Script Editor'

    def create_central_pane(self):
        return PythonEditorPane()


class PythonEditorPane(TaskPane):
    id = 'example.python_editor_pane'

    name = 'Python Editor'

    editor = Instance(PythonEditor)

    def create(self, parent):
        self.editor = PythonEditor(parent)
        self.control = self.editor.control

    def destroy(self):
        self.editor.destroy()
        self.control = self.editor = None
