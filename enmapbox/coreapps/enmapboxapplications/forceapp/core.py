import traceback
from qgis.core import *
from qgis.gui import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from enmapbox.gui.enmapboxgui import EnMAPBox
from enmapboxapplications.utils import loadUIFormClass
from hubflow.force import *

pathUi = join(dirname(__file__), 'ui')

class UiDB(QWidget, loadUIFormClass(pathUi=join(pathUi, 'db.ui'))):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.uiFolder().setStorageMode(QgsFileWidget.GetDirectory)

    def uiFolder(self):
        assert isinstance(self.uiFolder_, QgsFileWidget)
        return self.uiFolder_

class ForceApp(QMainWindow, loadUIFormClass(pathUi=join(pathUi, 'main.ui'))):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.uiDB().uiFolder().fileChanged.connect(self.updateDB)
        self.uiLevel().currentIndexChanged.connect(self.updateLevel)

        self.uiExecute_.clicked.connect(self.execute)

    def uiDB(self):
        assert isinstance(self.uiDB_, UiDB)
        return self.uiDB_

    def uiLevel(self):
        assert isinstance(self.uiLevel_, QComboBox)
        return self.uiLevel_

    def uiProduct(self):
        assert isinstance(self.uiProduct_, QComboBox)
        return self.uiProduct_

    def setDB(self, folder):
        self.uiDB().uiFolder().setFilePath(folder)

    def setLevel(self, levelNames):

        # Problem: Qt crashes when using QComboBox clear() or removeItem()
        # Workaround replace old ComboBox with a new and empty ComboBox
        self.uiLevel_.hide()
        self.uiLevel_ = QComboBox()
        self.uiLevelLayout_.addWidget(self.uiLevel_)
        self.uiLevel().addItems(levelNames)
        self.uiLevel().show()
        self.uiLevel().currentIndexChanged.connect(self.updateLevel)

    def setProduct(self, products):

        # Problem: Qt crashes when using QComboBox clear() or removeItem()
        # Workaround replace old ComboBox with a new and empty ComboBox
        self.uiProduct_.hide()
        self.uiProduct_ = QComboBox()
        self.uiProductLayout_.addWidget(self.uiProduct_)
        self.uiProduct().addItems(products)
        self.uiProduct().show()

    def updateDB(self, folder):

        if exists(folder):
            levelNames = ForceDB(folder=folder).levelNames()
        else:
            self.setLevel(levelNames=[])
            self.setProduct(products=[])
            return

        self.setLevel(levelNames=levelNames)
        self.updateLevel(levelIndex=0)

    def updateLevel(self, levelIndex):
        db = ForceDB(folder=self.uiDB().uiFolder().filePath())
        level = db.level(levelName=db.levelNames()[levelIndex])

        products = list()
        for tile in level.tiles():
            for raster in tile.collection().rasters():
                products.append(basename(raster.filename()))
            break # only look into first tile

        self.setProduct(products=products)

    def execute(self, *args):

        try:
            folder = self.uiDB().uiFolder().filePath()
            if exists(folder):
                db = ForceDB(folder=folder)
            else:
                return

            levelName = db.levelNames()[self.uiLevel().currentIndex()]

            product = splitext(self.uiProduct().currentText())
            filter = FileFilter(basenames=[product[0]], extensions=[product[1]])
            level = db.level(levelName=levelName, filters=[filter])
            filenames = list()

            for tile in level.tiles():
                rasters = list(tile.collection().rasters())
                if len(rasters) == 1:
                    filenames.append(rasters[0].filename())

            filename = '/vsimem/force/mosaik/{}.vrt'.format(product[0])
            rasterDataset = createVRTDataset(filename=filename, rasterDatasetsOrFilenames=filenames)
            rasterDataset.close()
            EnMAPBox.instance().addSource(source=filename)
        except:
            traceback.print_exc()