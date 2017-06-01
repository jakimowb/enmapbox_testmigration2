
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



if __name__ == '__main__':
    if True: sandboxWithEnMapBox(False)
    if False: sandboxGuiOnly()
