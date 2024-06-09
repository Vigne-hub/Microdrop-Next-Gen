# Local imports.
from .preferences import DeviceViewerPreferences

# Enthought library imports.
from envisage.ui.tasks.api import TasksApplication
from pyface.tasks.api import TaskWindowLayout
from traits.api import Bool, Instance, List, Property


class DeviceViewerApplication(TasksApplication):
    """Device Viewer application based on enthought envisage's The chaotic attractors Tasks application."""

    #### 'IApplication' interface #############################################

    # The application's globally unique identifier.
    id = "device_viewer.app"

    # The application's user-visible name.
    name = "Device Viewer App"

    #### 'TasksApplication' interface #########################################

    # The default window-level layout for the application.
    default_layout = List(TaskWindowLayout)

    # Whether to restore the previous application-level layout when the
    # applicaton is started.
    always_use_default_layout = Property(Bool)

    # above two traits are gotten from the preferences file

    #### 'Application' interface ####################################

    preferences_helper = Instance(DeviceViewerPreferences)

    ###########################################################################
    # Private interface.
    ###########################################################################

    #### Trait initializers ###################################################

    # note: The _default after a trait name to define a method is a convention to indicate that the trait is a
    # default value for another trait.

    def _default_layout_default(self):
        """
        Trait initializer for the default_layout task, which is the active task to be displayed. It is gotten from the
        preferences.

        """
        active_task = self.preferences_helper.default_task
        tasks = [factory.id for factory in self.task_factories]
        return [
            TaskWindowLayout(*tasks, active_task=active_task, size=(800, 600))
        ]

    def _preferences_helper_default(self):
        """
        Retireve the preferences from the preferences file using the DeviceViewerPreferences class.
        """
        return DeviceViewerPreferences(preferences=self.preferences)

    #### Trait property getter/setters ########################################

    # the _get and _set tags in the methods are used to define a getter and setter for a trait property.

    def _get_always_use_default_layout(self):
        return self.preferences_helper.always_use_default_layout
