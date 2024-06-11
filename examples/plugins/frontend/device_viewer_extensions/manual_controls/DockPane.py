# enthought imports
from traits.api import Instance
from pyface.tasks.api import TraitsDockPane

# local imports
from .MVC import ManualControlModel, ManualControlView, ManualControlControl

# This module's package.
PKG = '.'.join(__name__.split('.')[:-1])


class ManualControlsDockPane(TraitsDockPane):
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
