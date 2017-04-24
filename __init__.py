from enmapbox.utils.environment.SitePackageAppender import SitePackageAppender
SitePackageAppender.appendAll()

def classFactory(iface):
    from enmapboxplugin.EnMAPBoxPlugin import EnMAPBoxPlugin
    return EnMAPBoxPlugin(iface)
