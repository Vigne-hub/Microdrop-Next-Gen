from envisage.api import Application


class MyApp(Application):
    def __init__(self, plugins, broker=None):
        super(MyApp, self).__init__(plugins=plugins)

    print("#" * 100)
