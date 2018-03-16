import qgis
def sandboxWithEnMapBox(loadPF=False):
    from enmapbox.gui.utils import initQgisApplication, sandboxPureGui
    qgsApp = initQgisEnvironment()
    sandboxPureGui(loadProcessingFramework=loadPF)
    qgsApp.exec_()
    qgsApp.quit()

if __name__ == '__main__':
    sandboxWithEnMapBox(True)
