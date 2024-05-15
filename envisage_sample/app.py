from envisage.api import Application

from envisage_sample.Interfaces import IAnalysisService
from envisage_sample.frontend_plugins.ui_plugin import UIPlugin
from envisage_sample.frontend_plugins.plot_view_plugin import PlotViewPlugin
from envisage_sample.frontend_plugins.table_view_plugin import TableViewPlugin
from backend_plugins import AnalysisPlugin, LoggingPlugin


class MyApp(Application):
    def __init__(self, plugins):
        super(MyApp, self).__init__(plugins=plugins)


if __name__ == '__main__':
    plugins = [UIPlugin(), PlotViewPlugin(), TableViewPlugin(), AnalysisPlugin(), LoggingPlugin()]
    app = MyApp(plugins=plugins)
    app.start()

    # Accessing the views contributed by plugins
    ui_plugin = app.get_plugin('app.ui.plugin')
    print("Available views:", ui_plugin.views)

    # Accessing the analysis service provided by the backend
    analysis_service = app.get_service(protocol=IAnalysisService)
    if analysis_service:
        result = analysis_service.run_analysis("sample data")
        print("Analysis result:", result)

    app.stop()
