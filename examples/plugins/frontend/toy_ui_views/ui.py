from envisage.api import Plugin, ExtensionPoint
from traits.api import List

class UIPlugin(Plugin):
    id = 'app.ui.plugin'
    views = ExtensionPoint(List, id='app.ui.views')

    def start(self):
        super(UIPlugin, self).start()
        print("UI Plugin started with views:", self.views)

    def add_view(self, view):
        self.views.append(view)
