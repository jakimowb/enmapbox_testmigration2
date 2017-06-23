import os
global APP_DIR
APP_DIR = os.path.dirname(__file__)


def enmapboxApplications(enmapBox):

    from enmapboxintegration import MyEnMAPBoxApp
    return [MyEnMAPBoxApp(enmapBox)]

def classFactory(iface):

    return None