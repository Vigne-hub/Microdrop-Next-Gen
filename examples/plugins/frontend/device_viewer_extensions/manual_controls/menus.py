from pyface.tasks.action.api import SGroup, DockPaneAction

PKG = '.'.join(__name__.split('.')[:-1])
def menu_factory():
    """
    Create a menu for the Manual Controls
    The Sgroup is a list of actions that will be displayed in the menu.
    In this case there is only one action, the help menu.
    It is contributed to the manual controls dock pane using its show help method. Hence it is a DockPaneAction.
    It fetches the specified method from teh dock pane essentially.
    """
    return SGroup(
        DockPaneAction(
            id=PKG + ".help_menu",
            dock_pane_id=PKG + ".dock_pane",
            name="Manual Controls Help",
            method="show_help"
    ),
        id="example_help")