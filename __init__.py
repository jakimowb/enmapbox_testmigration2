from enmapbox.utils.environment.SitePackageAppender import SitePackageAppender
SitePackageAppender.appendAll()

def classFactory(iface):
    import EnMAPBoxPlugin
    return EnMAPBoxPlugin.EnMAPBoxPlugin(iface)
