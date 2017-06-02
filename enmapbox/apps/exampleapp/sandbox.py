import qgis
def sandboxWithEnMapBox(loadPF=False):
    """Minimum example to the this application"""
    from enmapbox.gui.sandbox import initQgisEnvironment, sandboxPureGui
    qgsApp = initQgisEnvironment()
    sandboxPureGui(loadProcessingFramework=loadPF)

    qgsApp.exec_()
    qgsApp.quit()


def sandboxGuiOnly():
    """Minimum example to the this application"""
    from enmapbox.gui.sandbox import initQgisEnvironment
    from ExampleApp import MyAppUserInterface

    qgsApp = initQgisEnvironment()
    ui = MyAppUserInterface()
    ui.exec_()
    qgsApp.exec_()
    qgsApp.quit()

def sandboxGuiOnlyNDVI():
    from enmapbox.gui.sandbox import initQgisEnvironment
    qgsApp = initQgisEnvironment()
    from gui import MyNDVIUserInterface
    ui = MyNDVIUserInterface()
    ui.show()
    qgsApp.exec_()
    qgsApp.quit()

if __name__ == '__main__':
    if False: sandboxGuiOnlyNDVI()
    if True: sandboxWithEnMapBox(True)
    if False: sandboxGuiOnly()
