from enmapbox.utils.environment.SitePackageAppender import SitePackageAppender
SitePackageAppender.appendAll()

def classFactory(iface):
    import enmapboxplugin
    return enmapboxplugin.EnMAPBoxPlugin(iface)
