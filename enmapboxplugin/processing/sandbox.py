import qgis
def sandboxWithEnMapBox(loadPF=False):
    from enmapbox.gui.sandbox import initQgisEnvironment, sandboxPureGui
    qgsApp = initQgisEnvironment()
    sandboxPureGui(loadProcessingFramework=loadPF)

    qgsApp.exec_()
    qgsApp.quit()

if __name__ == '__main__':
    if True: sandboxWithEnMapBox(True)
