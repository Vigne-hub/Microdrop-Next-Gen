# enthought imports
from pyface.tasks.api import TraitsDockPane
from traits.api import Instance
from traits.api import HasTraits, HTML
from traitsui.api import UItem, View, HTMLEditor

# Standard library imports.
import os.path

# Constants.
HELP_PATH = os.path.join(os.path.dirname(__file__), "help")

# local imports
from .MVC import ManualControlModel, ManualControlView, ManualControlControl

# This module's package.
PKG = '.'.join(__name__.split('.')[:-1])


class ManualControlsDockPane(TraitsDockPane):
    """
    A dock pane to set the voltage and frequency of the dropbot device.
    """
    #### 'ITaskPane' interface ################################################

    id = PKG + ".dock_pane"
    name = "Manual Controls Dock Pane"

    #### 'ManualControlsPane' interface ##########################################

    model = Instance(ManualControlModel)
    view = ManualControlView
    controller = Instance(ManualControlControl)

    # ---------------------- trait initializers ----------------

    def _model_default(self):
        return ManualControlModel()

    def _controller_default(self):
        return ManualControlControl()

    # ------------------------ trait change handlers ------------------------------------------
    def _controller_changed(self, new_controller):
        self.view.handler = new_controller

    def _view_changed(self, new_view):
        new_view.handler = self.controller

    def show_help(self):
        # Sample text to display as HTML: header, plus module docstring, plus
        # some lists. The docstring and lists will be auto-formatted
        # (format_text=True).
        sample_text = (
                """
            <html><body><h1>Manual Controls Help Page</h1>
    
            """
                + self.__doc__
        )

        class HTMLEditorDemo(HasTraits):
            """Defines the main HTMLEditor demo class."""

            # Define a HTML trait to view
            my_html_trait = HTML(sample_text)

            # Demo view
            traits_view = View(
                UItem(
                    'my_html_trait',
                    # we specify the editor explicitly in order to set format_text:
                    editor=HTMLEditor(format_text=False),
                ),
                title='HTMLEditor',
                buttons=['OK'],
                width=800,
                height=600,
                resizable=True,
            )

        # Create the demo:
        demo = HTMLEditorDemo()
        demo.configure_traits()
