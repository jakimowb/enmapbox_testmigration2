from enmapbox.utils.environment.SitePackageAppender import SitePackageAppender
SitePackageAppender.appendAll()

from enmapboxplugin.EnMAPBoxPlugin import EnMAPBoxPlugin

def classFactory(iface):
    return EnMAPBoxPlugin(iface)
