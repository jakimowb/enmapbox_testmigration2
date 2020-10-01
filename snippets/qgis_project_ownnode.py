import unittest
import os
from enmapbox.testing import EnMAPBoxTestCase
from qgis.core import *
from qgis.gui import *
from qgis.core import QgsLayerTreeGroup, QgsProject, QgsReadWriteContext
from qgis.gui import QgsLayerTreeView

from qgis.PyQt.QtCore import *

from qgis.PyQt.QtXml import *
from qgis.PyQt.QtGui import *
import tempfile

class MyLayerTreeGroup(QgsLayerTreeGroup):

    def __init__(self, name: str = 'MY_GROUP'):

        super().__init__(name=name, checked=False)
        self.n_calls : int = 0

    def clone(self):
        print(f'CLONE "{self.name()}"')
        grp = MyLayerTreeGroup(name=self.name())
        grp.n_calls = self.n_calls
        return grp

    def writeXml(self, parentElement: QDomElement, context: QgsReadWriteContext):
        # do not write anything!
        print('DO NOT WRITE XML FOR {}'.format(self.name()))

        self.n_calls += 1


import qgis.utils
ltv = qgis.utils.iface.layerTreeView()
assert isinstance(ltv, QgsLayerTreeView)
root: QgsLayerTreeGroup = ltv.model().rootGroup()
other_group = root.addGroup('OTHER_GROUP')
my_group: MyLayerTreeGroup = MyLayerTreeGroup()
root.addChildNode(my_group)

pj = QgsProject.instance()
assert isinstance(pj, QgsProject)
path = os.path.join(tempfile.gettempdir(), 'Test4.qgs')
path = r'C:\Users\geo_beja\Repositories\QGIS_Plugins\enmap-box\test-outputs\test.qgs'
pj.write(path)
#qgis.utils.iface.actionSaveProject().trigger()

with open(path, 'r') as f:
    xml = f.read()

    assert 'MY_GROUP' not in xml



