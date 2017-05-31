import os
from enmapbox.gui.applications import EnMAPBoxApplication
from PyQt4.QtGui import *

APP_DIR = os.path.dirname(__file__)


class MyEnMAPBoxApp(EnMAPBoxApplication):

    def __init__(self, enmapBox, parent=None):
        super(MyEnMAPBoxApp, self).__init__(enmapBox,parent=parent)
        self.name = 'My EnMAPBox App'
        self.version = 'Version 42'
        self.licence = 'BSD-3'
        s = ""

    def icon(self):
        pathIcon = os.path.join(APP_DIR, 'icon.png')
        return QIcon(pathIcon)

    def menu(self, appMenu):
        """
        Specify menu, submenus and actions
        :return:
        """
        menu = QMenu(self.name, appMenu)
        menu.setIcon(self.icon())

        #add QAction that starts your GUI
        a = menu.addAction('Show My GUI')
        a.triggered.connect(lambda : self.startExampleGUI())

        #add a submenu
        subMenu = menu.addMenu('Submenu')
        #add QAction to run another process
        a = subMenu.addAction('Start Process')
        a.triggered.connect(lambda : self.startExampleProcess('My App Action triggered'))

        return menu

    def geoAlgorithms(self):
        return None

    def startExampleGUI(self):
        ui = MyAppUI(self.enmapbox.ui)
        ui.setModal(False) #True = will block all other widget
        ui.show()

    def startExampleProcess(self, text):
        print('print something:')
        print(text)
        print('exampleProcess done')



from enmapbox.gui.utils import loadUIFormClass
pathUi = os.path.join(APP_DIR, 'example.ui')

class MyAppUI(QDialog, loadUIFormClass(pathUi)):
    """Constructor."""
    def __init__(self, parent=None):
        super(MyAppUI, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.initUiElements()
        self.radioButtonSet1.setChecked(True)
        self.updateSummary()

    def initUiElements(self):
        self.radioButtonSet1.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.radioButtonSet2.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.buttonBox.accepted.connect(self.updateSummary)



        #update summary if any parameter was changed
        self.stackedWidget.currentChanged.connect(self.updateSummary)
        self.colorButtonP1.colorChanged.connect(self.updateSummary)

        for spinBox in self.findChildren(QAbstractSpinBox):
            spinBox.editingFinished.connect(self.updateSummary)
        for comboBox in self.findChildren(QComboBox):
            comboBox.currentIndexChanged.connect(self.updateSummary)


    def updateSummary(self, *args):
        #read parameters
        from collections import OrderedDict
        params = OrderedDict()
        params['file'] = self.comboBoxMapLayer.currentLayer()

        if self.radioButtonSet1.isChecked():
            params['mode'] = 'mode 1'
            params['parameter 1'] = self.comboBoxP1.currentText()
            params['color '] = self.colorButtonP1.color().getRgb()

        elif self.radioButtonSet2.isChecked():
            params['mode'] = 'mode 2'
            params['parameter 1'] = self.doubleSpinBox.value()
            params['parameter 2'] = self.comboBoxP2.currentText()
        info = []
        for parameterName, parameterValue in params.items():
            info.append('{} = {}'.format(parameterName, parameterValue))

        self.textBox.setPlainText('\n'.join(info))


def sandboxWithEnMapBox():
    """Minimum example to the this application"""
    from enmapbox.gui.sandbox import initQgisEnvironment, sandboxPureGui
    qgsApp = initQgisEnvironment()
    sandboxPureGui(loadProcessingFramework=False)

    qgsApp.exec_()
    qgsApp.quit()


def sandboxGuiOnly():
    """Minimum example to the this application"""
    from enmapbox.gui.sandbox import initQgisEnvironment, sandboxPureGui
    qgsApp = initQgisEnvironment()
    ui = MyAppUI()
    ui.exec_()
    qgsApp.exec_()
    qgsApp.quit()


if __name__ == '__main__':
    if False: sandboxWithEnMapBox()
    if True: sandboxGuiOnly()