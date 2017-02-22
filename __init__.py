from site import addsitedir
from enmapbox import DIR_REPO, DIR_SITE_PACKAGES, DIR_SITE_PACKAGES_OS_SPECIFIC

for sitedir in [DIR_REPO, DIR_SITE_PACKAGES, DIR_SITE_PACKAGES_OS_SPECIFIC]:
    addsitedir(sitedir)


PROCESSING_ONLY = True

def classFactory(iface):

    if PROCESSING_ONLY:
        from enmapbox.processing.Plugin import Plugin
        return Plugin(iface)
    else:
        from enmapboxplugin import EnMAPBoxPlugin
        return EnMAPBoxPlugin(iface)