import sys, os


def writelogmessage(message, tag, level):
    print('{}({}): {}'.format( tag, level, message ) )
from qgis.core import QgsMessageLog
QgsMessageLog.instance().messageReceived.connect( writelogmessage)


def test_GUI():
    os.environ['QGIS_DEBUG'] = '1'
    import enmapbox
    enmapbox.DEBUG = True
    import enmapbox.main
    enmapbox.main.moduletest()



if __name__ == '__main__':
    if True: test_GUI()