from apptools.preferences.api import PreferencesHelper
from traits.api import Bool, Dict, Str
from traitsui.api import EnumEditor, HGroup, Item, Label, VGroup, View

# Enthought library imports.
from envisage.ui.tasks.api import PreferencesPane


class DeviceViewerPreferences(PreferencesHelper):
    """The preferences helper, inspired by envisage one for the Attractors application."""

    #### 'PreferencesHelper' interface ########################################

    # The path to the preference node that contains the preferences.
    preferences_path = "device_viewer"

    #### Preferences ##########################################################

    # The task to activate on app startup if not restoring an old layout.
    default_task = Str

    # Whether to always apply the default application-level layout.
    # See TasksApplication for more information.
    always_use_default_layout = Bool


class DeviceViewerPreferencesPane(PreferencesPane):
    """Device Viewer preferences pane based on enthought envisage's The preferences pane for the Attractors application."""

    #### 'PreferencesPane' interface ##########################################

    # The factory to use for creating the preferences model object.
    model_factory = DeviceViewerPreferences

    #### 'AttractorsPreferencesPane' interface ################################

    view = View(
        VGroup(
            HGroup(
                Item("always_use_default_layout"),
                Label("Always use the default active task on startup"),
                show_labels=False,
            ),
            label="Application startup",
        ),
        resizable=True,
    )

    ###########################################################################
    # Private interface.
    ###########################################################################
