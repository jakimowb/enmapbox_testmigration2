#we need to add more comments here
#from enmapbox.utils.environment.SitePackageAppender import SitePackageAppender
#SitePackageAppender.appendAll()

def classFactory(iface):
    """
    Loads the EnMAP-Box Plugin
    :param iface:
    :return: enmapboxplugin.EnMAPBoxPlugin(iface)
    """
    import os, sys
    d = os.path.dirname(__file__)
    added = []
    if not d in sys.path:
        sys.path.append(d)
        added.append(d)
    try:
        from enmapbox.enmapboxplugin import EnMAPBoxPlugin
        plugin = EnMAPBoxPlugin(iface)
    except Exception as ex:
        for path in added:
            sys.path.remove(path)
        raise ex
    return plugin
