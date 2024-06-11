from pyface.tasks.action.api import SGroup, DockPaneAction

PKG = '.'.join(__name__.split('.')[:-1])
def menu_factory():
    return SGroup(
        DockPaneAction(
            id=PKG + ".help_menu",
            dock_pane_id=PKG + ".dock_pane",
            name="Manual Controls Help",
            method="show_help"
    ),
        id="example_help")