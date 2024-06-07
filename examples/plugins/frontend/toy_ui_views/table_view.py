from envisage.api import Plugin
from traits.api import List

class TableViewPlugin(Plugin):
    id = 'app.table.view.plugin'
    views = List(contributes_to='app.ui.views')

    def start(self):
        super(TableViewPlugin, self).start()
        self.views.append('Table View')
        print("Table View Plugin started and contributed a view.")
