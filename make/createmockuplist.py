



import sys, os, re
from enmapbox import DIR_REPO

pathList = os.path.join(DIR_REPO, *['doc','source','mockednameslist.txt'])
import qgis.PyQt.QtCore
import qgis.gui
import qgis.core
mockedNames = []

import qgis.core, qgis, qgis.PyQt.QtCore, qgis.PyQt.QtGui, qgis.PyQt.QtWidgets, qgis.PyQt.Qt
modules = [k for k in sys.modules.keys() if re.search('(qgis|Qt)', k)]
for name in modules:
    #mockedNames.append(name)
    module = sys.modules[name]
    for member in dir(module):
        if not member.startswith('Qgs'):
            continue
        mockedName = '{}.{}'.format(name, member)
        if '__' in mockedName :
            continue
        mockedNames.append(mockedName)
        #mockedNames.append(member)


f = open(pathList, 'w', encoding='utf-8')
f.write('\n'.join(mockedNames))
f.close()
print('\n'.join(mockedNames))