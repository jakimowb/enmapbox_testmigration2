from enmapbox.utils.environment.SitePackageAppender import SitePackageAppender
from enmapbox.utils.environment.DependencyChecker import DependencyChecker
SitePackageAppender.appendAll()

modules = ['matplotlib', 'sklearn']
modules.extend(['html', 'HTML', 'pyqtgraph', 'markup', 'rios', 'tabulate', 'unipath', 'units', 'yaml'])
DependencyChecker.importAllDependencies(modules)


def classFactory(iface):
    from enmapboxplugin.EnMAPBoxPlugin import EnMAPBoxPlugin
    return EnMAPBoxPlugin(iface)
