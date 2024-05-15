from envisage.api import Plugin
from traits.api import List

class PlotViewPlugin(Plugin):
    id = 'app.plot.view.plugin'
    views = List(contributes_to='app.ui.views')

    def start(self):
        super(PlotViewPlugin, self).start()
        self.views.append('Plot View')
        print("Plot View Plugin started and contributed a view.")
