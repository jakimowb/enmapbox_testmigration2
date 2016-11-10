if __name__ == '__main__':
    import enmapbox
    enmapbox.DEBUG = True
    import enmapbox.main
    enmapbox.main.moduletest()

import sys, os

os.environ['QGIS_DEBUG'] = '1'

def writelogmessage(message, tag, level):
    print('{}({}): {}'.format( tag, level, message ) )
from qgis.core import QgsMessageLog
QgsMessageLog.instance().messageReceived.connect( writelogmessage)