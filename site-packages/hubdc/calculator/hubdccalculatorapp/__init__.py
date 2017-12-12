import os
APP_DIR = os.path.dirname(__file__)

def enmapboxApplicationFactory(enmapBox):
    from .enmapboxintegration import HubDatacubeCalculatorApp
    return [HubDatacubeCalculatorApp(enmapBox)]
