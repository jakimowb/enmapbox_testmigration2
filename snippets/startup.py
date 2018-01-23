



if __name__ == '__main__':

    from enmapbox.gui.utils import initQgisApplication
    from enmapbox.gui.enmapboxgui import EnMAPBox

    qgsApp = initQgisApplication()
    enmapBox = EnMAPBox(None)
    enmapBox.openExampleData(mapWindows=1)

    qgsApp.exec_()
    qgsApp.quit()
