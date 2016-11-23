import site, sys, os, inspect

from qgis import *
from qgis.core import *
from qgis.gui import *
from PyQt4.QtGui import *
from PyQt.QtCore import *


from enmapbox import jp, DIR_UI

from enmapbox.utils import loadUIFormClass

#directory of 'xyz.ui' files. change if necessary
DIR_UI = os.path.normpath(os.path.split(inspect.getfile(inspect.currentframe()))[0])

class TemplateDialogUI(QDialog,
        loadUIFormClass(os.path.normpath(jp(DIR_UI, 'template_dialog.ui')),
                                   )):

    sigApply = pyqtSignal(object)

    def __init__(self, parent=None):
        """Constructor."""
        title = 'Dialog Template'
        super(TemplateDialogUI, self).__init__(parent, Qt.Dialog)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use auto connect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        #connect signals to (self defined) slots to implemente frontend-logic

        #note: buttonbar signals connected via Qt Designer in *.ui file

        self.accepted.connect(self.onAccept)
        self.rejected.connect(self.onCancel)

        self.buttonBox.button(QDialogButtonBox.Apply).clicked.connect(self.onApply)
        self.my_result = None

    def onApply(self):
        # implement what to do if user clicked on apply button
        print('Apply')
        self.sigApply.emit(['my','apply','results'])


    def onAccept(self):
        # implement what to do if user clicked on accept button
        print('Accepted')
        self.my_result = 'my results'

    def onCancel(self):

        # implement what to do if user clicked on cancel button
        self.my_result = 'canceled. no results returned'
        print('Canceled')



def handleDialogSignals(info, data):

    print('Got data from dialog on {}: {}'.format(info,str(data)))



if __name__ == '__main__':


    # add site-packages to sys.path as done by enmapboxplugin.py
    jp = os.path.join
    from enmapbox import DIR_SITE_PACKAGES
    site.addsitedir(DIR_SITE_PACKAGES)


    # run tests
    PATH_QGS = os.environ['QGIS_PREFIX_PATH']
    qgsApp = QgsApplication([], True)
    qgsApp.setPrefixPath(PATH_QGS, True)
    qgsApp.initQgis()

    #use model -> blocking dialog
    D = TemplateDialogUI()
    result = D.exec_()
    if result == QDialog.Rejected:
        print('Canceled Dialog Result: ' + str(D.my_result))
    if result == QDialog.Accepted:
        print('Accepted Dialog Result: ' + str(D.my_result))




    #use modeless -> non blocking dialog
    #use signal to react on pressed buttons
    D.sigApply.connect(lambda data: handleDialogSignals('apply', data))
    D.rejected.connect(lambda : handleDialogSignals('canceled', D.my_result))
    D.accepted.connect(lambda : handleDialogSignals('accepted', D.my_result))

    D.show()
    D.raise_()
    D.activateWindow()

    qgsApp.exec_()




    qgsApp.exitQgis()

